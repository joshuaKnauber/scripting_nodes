"""Stdlib JSON-RPC 2.0 over HTTP, exposing the MCP Streamable-HTTP transport.

The server binds 127.0.0.1 only (loopback), runs in a daemon thread, and
hands every tool body to `bridge.call_on_main` so bpy access happens on
Blender's main thread.

Scope: the methods needed by current MCP clients (initialize, tools/list,
tools/call, ping). Tools change the open file and run Python. No sessions, no SSE.

Security: loopback alone isn't enough - any web page open in a browser can
POST to 127.0.0.1. Requests are rejected unless they look like they come from
a local MCP client: no browser `Origin`, a loopback `Host` (blocks DNS
rebinding) and a JSON content type (forces a CORS preflight we never answer).
"""

import base64
import hmac
import json
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import bpy

from ..core import scheduler
from ..lib.version import addon_version
from ..settings.preferences import get_preferences
from . import bridge
from .tools import TOOLS, Image, Later
from .tools._common import ToolError


# Latest MCP revision this server speaks. Clients negotiate down on initialize.
PROTOCOL_VERSION = "2025-06-18"
SERVER_INFO = {"name": "scripting-nodes", "version": addon_version()}

# How long a tool call may block waiting for Blender's main thread to pick
# it up. Codegen for a big tree can be a few seconds; 30s is a generous
# upper bound that still surfaces real hangs.
TOOL_TIMEOUT_SECONDS = 60.0


_LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _is_loopback_url(url: str) -> bool:
    from urllib.parse import urlparse

    try:
        return urlparse(url).hostname in _LOOPBACK_HOSTS
    except ValueError:
        return False


_SERVER: "ThreadingHTTPServer | None" = None
# bearer token required when set (preferences), read when the server starts
_TOKEN = ""
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


INSTRUCTIONS = """Scripting Nodes builds Blender add-ons from node graphs: each node
tree becomes a module of the add-on, rebuilt and reloaded on every change.
Start with get_addon. Find nodes with list_node_types / get_node_type, build
with create_tree and edit_tree (many nodes and links per call), define
properties with edit_properties and functions with edit_function. After
changes, get_problems tells what's missing or broken; get_code shows the
generated Python; run_operator tries an operator; screenshot shows Blender
as the user sees it. run_python does anything else in Blender."""


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
            "instructions": INSTRUCTIONS,
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


def _run_tool(fn, args, name="", writes=False):
    """Runs on the main thread: the tool, then any regeneration it caused, so
    the result (and the next tool call) sees up-to-date code. Changes are one
    undo step each."""
    try:
        result = fn(**args)
    except TypeError as exc:
        if "argument" in str(exc) and fn.__name__ in str(exc):
            raise ToolError(f"{exc}. See the tool's input schema.") from exc
        raise
    scheduler.flush()
    if writes and not bpy.app.background:
        window = bpy.context.window_manager.windows[0]
        try:
            with bpy.context.temp_override(window=window):
                bpy.ops.ed.undo_push(message=f"MCP: {name}")
        except RuntimeError:
            pass  # nothing to push in this state
    return result


def _content(result):
    if isinstance(result, Image):
        content = [
            {
                "type": "image",
                "data": base64.b64encode(result.data).decode("ascii"),
                "mimeType": result.mime,
            }
        ]
        if result.text:
            content.append({"type": "text", "text": result.text})
        return content
    text = json.dumps(result, ensure_ascii=False, default=str)
    return [{"type": "text", "text": text}]


def _handle_tools_call(req_id, params):
    name = (params or {}).get("name")
    args = (params or {}).get("arguments") or {}
    if name not in TOOLS:
        return _err(req_id, -32602, f"Unknown tool: {name!r}")
    spec = TOOLS[name]
    try:
        result = bridge.call_on_main(
            _run_tool,
            spec["fn"],
            args,
            name,
            spec["writes"],
            timeout=TOOL_TIMEOUT_SECONDS,
        )
        while isinstance(result, Later):
            time.sleep(result.delay)  # Blender draws meanwhile
            result = bridge.call_on_main(result.then, timeout=TOOL_TIMEOUT_SECONDS)
        return _ok(req_id, {"content": _content(result)})
    except Exception as exc:
        text = (
            str(exc) if isinstance(exc, ToolError) else f"{type(exc).__name__}: {exc}"
        )
        return _ok(
            req_id, {"content": [{"type": "text", "text": text}], "isError": True}
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

    def _reject_reason(self):
        """Return why this request must be refused, or None if it's allowed."""
        token = _TOKEN
        if token:
            sent = self.headers.get("Authorization") or ""
            if not hmac.compare_digest(sent, f"Bearer {token}"):
                return "missing or wrong token"
        origin = self.headers.get("Origin")
        if origin and not _is_loopback_url(origin):
            return f"origin {origin!r} not allowed"
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]")
        if host not in _LOOPBACK_HOSTS:
            return f"host {host!r} not allowed"
        content_type = (self.headers.get("Content-Type") or "").split(";")[0]
        if content_type.strip().lower() != "application/json":
            return "Content-Type must be application/json"
        return None

    def do_POST(self):
        reason = self._reject_reason()
        if reason:
            self.log_message("rejected request: %s", reason)
            self._send_json(403, {"error": reason})
            return
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
    global _SERVER, _THREAD, _TOKEN
    if is_running():
        raise RuntimeError("MCP server is already running")
    try:
        _TOKEN = get_preferences().mcp_token.strip()
    except (AttributeError, KeyError):
        _TOKEN = ""
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


def register():
    """Start with Blender if the preferences say so (not in background mode,
    where there's no one to connect)."""
    if bpy.app.background:
        return

    def start_later():
        try:
            prefs = get_preferences()
            if prefs.mcp_autostart and not is_running():
                start(prefs.mcp_port)
        except Exception as exc:  # noqa: BLE001 - a busy port mustn't break loading
            print(f"[SN MCP] could not start: {exc}")

    bpy.app.timers.register(start_later, first_interval=1.0)


def unregister():
    """auto_load hook — make sure we don't leave a port bound at unload."""
    if is_running():
        stop()
