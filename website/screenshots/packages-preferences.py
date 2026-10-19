"""The Node Packages box in Scripting Nodes' preferences, with the example
package (website/public/downloads/clipboard_tools.zip) installed."""

import os

import addon_utils
import bpy
import helpers

ZIP = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "public",
    "downloads",
    "clipboard_tools.zip",
)

WINDOW_SIZE = (900, 620)
AREA_ONLY = True
FRAME = "bottom"
CROP = (0, 0, 1, 0.765)


def setup():
    helpers.sn("src.core.node_packages").install(ZIP)
    # what Install does on its timer: reload Scripting Nodes with the package
    helpers.disable_addon()
    helpers.enable_addon()
    return None


def after(context):
    window = context.window_manager.windows[0]
    area = max(window.screen.areas, key=lambda a: a.width * a.height)
    area.type = "PREFERENCES"
    context.preferences.active_section = "ADDONS"
    context.window_manager.addon_search = "Scripting Nodes"
    for mod in addon_utils.modules():
        if mod.__name__ == helpers.ADDON_MODULE:
            addon_utils.module_bl_info(mod)["show_expanded"] = True
