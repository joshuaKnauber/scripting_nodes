import json

import bpy

from ...settings.preferences import get_preferences
from .. import server


SERVER_NAME = "scripting-nodes"


def _server_url(port: int) -> str:
    return f"http://127.0.0.1:{port}/"


def _token():
    return get_preferences().mcp_token.strip()


def _snippet_claude_code(port: int) -> str:
    command = f"claude mcp add --transport http {SERVER_NAME} {_server_url(port)}"
    if _token():
        command += f' --header "Authorization: Bearer {_token()}"'
    return command


def _snippet_codex(port: int) -> str:
    # ~/.codex/config.toml stanza. Codex reads HTTP MCP servers via the `url` key.
    snippet = f'[mcp_servers.{SERVER_NAME}]\nurl = "{_server_url(port)}"\n'
    if _token():
        snippet += f'http_headers = {{ Authorization = "Bearer {_token()}" }}\n'
    return snippet


def _snippet_claude_desktop(port: int) -> str:
    # claude_desktop_config.json only starts local (stdio) servers: mcp-remote
    # bridges to the HTTP server. -y: npx mustn't wait for an install prompt.
    # The header goes through env, mcp-remote's way to pass one with a space.
    server = {"command": "npx", "args": ["-y", "mcp-remote", _server_url(port)]}
    if _token():
        server["args"] += ["--header", "Authorization:${SN_MCP_AUTH}"]
        server["env"] = {"SN_MCP_AUTH": f"Bearer {_token()}"}
    return json.dumps({"mcpServers": {SERVER_NAME: server}}, indent=2)


def _snippet_json(port: int) -> str:
    server = {"type": "http", "url": _server_url(port)}
    if _token():
        server["headers"] = {"Authorization": f"Bearer {_token()}"}
    return json.dumps({"mcpServers": {SERVER_NAME: server}}, indent=2)


_SNIPPET_BUILDERS = {
    "CLAUDE_CODE": _snippet_claude_code,
    "CODEX": _snippet_codex,
    "CLAUDE_DESKTOP": _snippet_claude_desktop,
    "JSON": _snippet_json,
}

_TARGET_LABELS = {
    "CLAUDE_CODE": "Claude Code",
    "CODEX": "Codex",
    "CLAUDE_DESKTOP": "Claude Desktop",
    "JSON": "JSON",
}


class SNA_OT_StartMCPServer(bpy.types.Operator):
    """Start the Scripting Nodes MCP server on the configured port"""

    bl_idname = "sna.start_mcp_server"
    bl_label = "Start MCP Server"
    bl_options = {"REGISTER", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        return not server.is_running()

    def execute(self, context):
        port = get_preferences().mcp_port
        try:
            server.start(port)
        except OSError as exc:
            self.report(
                {"ERROR"},
                f"Failed to bind port {port}: {exc.strerror or exc}",
            )
            return {"CANCELLED"}
        except Exception as exc:
            self.report({"ERROR"}, f"Failed to start MCP server: {exc}")
            return {"CANCELLED"}
        self.report({"INFO"}, f"MCP server listening on http://127.0.0.1:{port}/")
        return {"FINISHED"}


class SNA_OT_StopMCPServer(bpy.types.Operator):
    """Stop the Scripting Nodes MCP server"""

    bl_idname = "sna.stop_mcp_server"
    bl_label = "Stop MCP Server"
    bl_options = {"REGISTER", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        return server.is_running()

    def execute(self, context):
        server.stop()
        self.report({"INFO"}, "MCP server stopped")
        return {"FINISHED"}


class SNA_OT_CopyMCPSnippet(bpy.types.Operator):
    """Copy a client-install snippet for this MCP server to the clipboard"""

    bl_idname = "sna.copy_mcp_snippet"
    bl_label = "Copy MCP Install Snippet"
    bl_options = {"REGISTER", "INTERNAL"}

    target: bpy.props.EnumProperty(
        name="Target",
        items=[
            (
                "CLAUDE_CODE",
                "Claude Code",
                "Shell command for `claude mcp add` registering this server over HTTP",
            ),
            (
                "CODEX",
                "Codex",
                "TOML stanza to paste into ~/.codex/config.toml",
            ),
            (
                "CLAUDE_DESKTOP",
                "Claude Desktop",
                "mcpServers entry for claude_desktop_config.json (needs Node.js: "
                "it connects through mcp-remote)",
            ),
            (
                "JSON",
                "JSON",
                "mcpServers entry for clients that connect over HTTP (Cursor, ...)",
            ),
        ],
        default="CLAUDE_CODE",
    )

    def execute(self, context):
        port = get_preferences().mcp_port
        builder = _SNIPPET_BUILDERS.get(self.target)
        if builder is None:
            self.report({"ERROR"}, f"Unknown snippet target: {self.target}")
            return {"CANCELLED"}
        snippet = builder(port)
        context.window_manager.clipboard = snippet
        self.report(
            {"INFO"},
            f"Copied {_TARGET_LABELS[self.target]} install snippet to clipboard",
        )
        return {"FINISHED"}
