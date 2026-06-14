import json

import bpy

from ...settings.addon_settings.preferences import get_preferences
from .. import server


SERVER_NAME = "scripting-nodes"


def _server_url(port: int) -> str:
    return f"http://127.0.0.1:{port}/"


def _snippet_claude_code(port: int) -> str:
    return f"claude mcp add --transport http {SERVER_NAME} {_server_url(port)}"


def _snippet_codex(port: int) -> str:
    # ~/.codex/config.toml stanza. Codex reads HTTP MCP servers via the `url` key.
    return (
        f"[mcp_servers.{SERVER_NAME}]\n"
        f'url = "{_server_url(port)}"\n'
    )


def _snippet_json(port: int) -> str:
    return json.dumps(
        {
            "mcpServers": {
                SERVER_NAME: {
                    "type": "http",
                    "url": _server_url(port),
                }
            }
        },
        indent=2,
    )


_SNIPPET_BUILDERS = {
    "CLAUDE_CODE": _snippet_claude_code,
    "CODEX": _snippet_codex,
    "JSON": _snippet_json,
}

_TARGET_LABELS = {
    "CLAUDE_CODE": "Claude Code",
    "CODEX": "Codex",
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
                "JSON",
                "JSON",
                "Generic mcpServers JSON entry (Claude Desktop and similar clients)",
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
