"""Stdlib JSON-RPC 2.0 over HTTP, exposing the MCP Streamable-HTTP transport.

The server binds 127.0.0.1 only (loopback), runs in a daemon thread, and
hands every tool body to `bridge.call_on_main` so bpy access happens on
Blender's main thread.

Scope: read-only methods needed by current MCP clients (initialize,
tools/list, tools/call, ping). No sessions, no SSE streaming.
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import json
import traceback

from . import bridge
from .tools import TOOLS


# Latest MCP revision this server speaks. Clients negotiate down on initialize.
PROTOCOL_VERSION = "2025-06-18"
SERVER_INFO = {"name": "scripting-nodes", "version": "4.0.0"}

# How long a tool call may block waiting for Blender's main thread to pick
# it up. Codegen for a big tree can be a few seconds; 30s is a generous
# upper bound that still surfaces real hangs.
TOOL_TIMEOUT_SECONDS = 30.0


_SERVER: "ThreadingHTTPServer | None" = None
_THREAD: "Thread | None" = None


# ---------------------------------------------------------------------------
# JSON-RPC dispatch
# ---------------------------------------------------------------------------


def _ok(req_id, result):
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _err(req_id, code, message, data=None):
    err = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": "2.0", "id": req_id, "error": err}


def _handle_initialize(req_id, params):
    # We accept the client's requested protocolVersion verbatim if it's a
    # version we recognize; otherwise we advertise our own and let the
    # client decide whether to proceed.
    return _ok(
        req_id,
        {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": SERVER_INFO,
        },
    )


def _handle_tools_list(req_id, params):
    tools = [
        {
            "name": name,
            "description": spec["description"],
            "inputSchema": spec["inputSchema"],
        }
        for name, spec in TOOLS.items()
    ]
    return _ok(req_id, {"tools": tools})


def _handle_tools_call(req_id, params):
    name = (params or {}).get("name")
    args = (params or {}).get("arguments") or {}
    if name not in TOOLS:
        return _err(req_id, -32602, f"Unknown tool: {name!r}")
    fn = TOOLS[name]["fn"]
    try:
        result = bridge.call_on_main(fn, timeout=TOOL_TIMEOUT_SECONDS, **args)
        text = json.dumps(result, indent=2, default=str)
        return _ok(req_id, {"content": [{"type": "text", "text": text}]})
    except Exception as exc:
        return _ok(
            req_id,
            {
                "content": [
                    {"type": "text", "text": f"{type(exc).__name__}: {exc}"}
                ],
                "isError": True,
            },
        )


_METHODS = {
    "initialize": _handle_initialize,
    "tools/list": _handle_tools_list,
    "tools/call": _handle_tools_call,
    "ping": lambda req_id, params: _ok(req_id, {}),
}


def _dispatch(message):
    """Route a parsed JSON-RPC message. Returns a response dict, or None
    for notifications (no id → no reply per JSON-RPC 2.0)."""
    req_id = message.get("id")
    method = message.get("method")
    params = message.get("params")
    # Notifications (no id) — MCP uses these for `notifications/initialized`
    # and similar housekeeping. We accept and ignore.
    if req_id is None:
        return None
    handler = _METHODS.get(method)
    if handler is None:
        return _err(req_id, -32601, f"Method not found: {method!r}")
    try:
        return handler(req_id, params)
    except Exception as exc:
        return _err(
            req_id,
            -32603,
            f"Internal error: {type(exc).__name__}: {exc}",
            data=traceback.format_exc(),
        )


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------


class _Handler(BaseHTTPRequestHandler):

    # Quiet the default per-request stderr log — re-route everything through
    # a single SN-prefixed channel.
    def log_message(self, format, *args):
        print(f"[SN MCP] {self.address_string()} - " + (format % args))

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_empty(self, status):
        self.send_response(status)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        # No server-initiated SSE stream — clients should POST. Some clients
        # probe GET first; respond cleanly.
        self._send_empty(405)

    def do_DELETE(self):
        # Session termination on Streamable HTTP. We're stateless, so just ack.
        self._send_empty(204)

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length == 0:
            self._send_json(400, {"error": "empty body"})
            return
        try:
            raw = self.rfile.read(length)
            message = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._send_json(
                400,
                {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {exc}"},
                },
            )
            return

        # Single message or batch?
        if isinstance(message, list):
            responses = [r for r in (_dispatch(m) for m in message) if r is not None]
            if not responses:
                self._send_empty(202)
                return
            self._send_json(200, responses)
            return

        response = _dispatch(message)
        if response is None:
            # Notification — JSON-RPC says no response body.
            self._send_empty(202)
            return
        self._send_json(200, response)


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------


def is_running() -> bool:
    return _THREAD is not None and _THREAD.is_alive()


def start(port: int) -> None:
    """Bring the server up on localhost:`port`. Raises OSError on bind failure."""
    global _SERVER, _THREAD
    if is_running():
        raise RuntimeError("MCP server is already running")
    bridge.start_pump()
    _SERVER = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    # Daemon thread so a crashed/forgotten server doesn't block Blender exit.
    _THREAD = Thread(
        target=_SERVER.serve_forever,
        name=f"SN-MCP-Server-{port}",
        daemon=True,
    )
    _THREAD.start()
    print(f"[SN MCP] server listening on http://127.0.0.1:{port}/")


def stop() -> None:
    """Shut down cleanly. Idempotent."""
    global _SERVER, _THREAD
    if _SERVER is not None:
        try:
            _SERVER.shutdown()
            _SERVER.server_close()
        except Exception as exc:
            print(f"[SN MCP] error during shutdown: {exc}")
    if _THREAD is not None:
        _THREAD.join(timeout=5.0)
    _SERVER = None
    _THREAD = None
    bridge.stop_pump()
    print("[SN MCP] server stopped")


def unregister():
    """auto_load hook — make sure we don't leave a port bound at unload."""
    if is_running():
        stop()
