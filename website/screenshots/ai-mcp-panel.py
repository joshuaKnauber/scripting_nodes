"""The MCP Server panel in the node editor's sidebar, server stopped."""

import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _publishing  # noqa: E402
import helpers  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (1000, 760)
CROP = (0.663, 0, 1, 0.885)  # the sidebar, down to the MCP Server panel
FRAME = "float"


def open_mcp_panel():
    """The panel starts closed, below the Addon and Files panels: register
    it open and first, so it's in view."""
    panel = helpers.sn("src.mcp_server.ui.panel").SNA_PT_MCPServer
    bpy.utils.unregister_class(panel)
    panel.bl_options = set(panel.bl_options) - {"DEFAULT_CLOSED"}
    panel.bl_order = -1  # first, above the Addon panel
    bpy.utils.register_class(panel)


def setup():
    open_mcp_panel()
    return _publishing.build()


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            for region in area.regions:
                if region.type == "UI":
                    region.tag_redraw()
