from scripting_nodes.src.lib.constants.paths import DEV_ADDON_MODULE
from .modules.modules import (
    reload_addon,
    unregister_module,
)
from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import has_addon
from .generator import generate_addon, has_changes
import bpy


def watch_changes():
    if has_changes() and has_addon():
        if bpy.context.scene.sna.addon.enabled:
            generate_addon()
            reload_addon(DEV_ADDON_MODULE)
        else:
            unregister_module(DEV_ADDON_MODULE)

    if bpy.context.scene.sna.addon.force_production:
        return 2
    elif has_addon() or not bpy.context.scene.sna.addon.enabled:
        return 0.25
    return 1
