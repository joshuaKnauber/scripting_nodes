import bpy
from bpy.types import AddonPreferences


# the add-on's package (this module is in <package>.src.settings)
_addon_name = __package__.rsplit(".src.", 1)[0]


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

    mcp_autostart: bpy.props.BoolProperty(
        name="Start with Blender",
        description="Start the MCP server when Blender starts",
    )
    mcp_allow_python: bpy.props.BoolProperty(
        name="Allow Running Python",
        description=(
            "Let MCP clients run Python in Blender (run_python). Any program "
            "on this computer that can reach the port could then run code"
        ),
        default=True,
    )
    mcp_token: bpy.props.StringProperty(
        name="Token",
        description=(
            "Optional: clients must send it (Authorization: Bearer <token>). "
            "Read when the server starts"
        ),
        subtype="PASSWORD",
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="MCP Server", icon="PLUGIN")
        col = box.column()
        col.use_property_split = True
        col.prop(self, "mcp_port")
        col.prop(self, "mcp_autostart")
        col.prop(self, "mcp_allow_python")
        col.prop(self, "mcp_token")
        col.label(
            text="Start/stop the server from the node editor sidebar (N panel).",
            icon="INFO",
        )


def get_preferences() -> SNA_AddonPreferences:
    """Get the addon preferences"""
    return bpy.context.preferences.addons[_addon_name].preferences
