import bpy
from bpy.types import AddonPreferences


def _get_addon_name():
    """Get the addon name for bl_idname.

    For extensions: bl_ext.<repo>.<name> -> bl_ext.<repo>.<name>
    For legacy addons: scripting_nodes.src... -> scripting_nodes
    """
    parts = __package__.split(".")
    if parts[0] == "bl_ext" and len(parts) >= 3:
        return ".".join(parts[:3])
    else:
        return parts[0]


_addon_name = _get_addon_name()


class SNA_AddonPreferences(AddonPreferences):
    """Scripting Nodes addon preferences"""

    bl_idname = _addon_name

    mcp_port: bpy.props.IntProperty(
        name="MCP Server Port",
        description="TCP port the MCP server listens on (localhost only)",
        default=7423,
        min=1024,
        max=65535,
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="MCP Server", icon="PLUGIN")
        col = box.column()
        col.use_property_split = True
        col.prop(self, "mcp_port")
        col.label(
            text="Start/stop the server from the node editor sidebar (N panel).",
            icon="INFO",
        )


def get_preferences() -> SNA_AddonPreferences:
    """Get the addon preferences"""
    return bpy.context.preferences.addons[_addon_name].preferences
