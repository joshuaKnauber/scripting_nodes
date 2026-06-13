import bpy

from ....lib.editor.editor import in_sn_tree
from ...settings.addon_settings.preferences import get_preferences
from .. import server


class SNA_PT_MCPServer(bpy.types.Panel):
    bl_idname = "SNA_PT_MCPServer"
    bl_label = "MCP Server"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 5

    @classmethod
    def poll(cls, context):
        return in_sn_tree(context)

    def draw(self, context):
        layout = self.layout
        prefs = get_preferences()
        running = server.is_running()

        row = layout.row(align=True)
        if running:
            row.label(text=f"Running on :{prefs.mcp_port}", icon="CHECKMARK")
        else:
            row.label(text="Stopped", icon="X")

        row = layout.row(align=True)
        row.scale_y = 2.0
        if running:
            row.operator("sna.stop_mcp_server", text="Stop", icon="PAUSE")
        else:
            row.operator("sna.start_mcp_server", text="Start", icon="PLAY")

        copy_row = layout.row(align=True)
        op = copy_row.operator(
            "sna.copy_mcp_snippet", text="Claude Code", icon="COPYDOWN"
        )
        op.target = "CLAUDE_CODE"
        op = copy_row.operator("sna.copy_mcp_snippet", text="Codex", icon="COPYDOWN")
        op.target = "CODEX"
        op = copy_row.operator("sna.copy_mcp_snippet", text="JSON", icon="COPYDOWN")
        op.target = "JSON"

        col = layout.column()
        col.use_property_split = True
        col.enabled = not running
        col.prop(prefs, "mcp_port", text="Port")
