from ....lib.utils.screen.screen import redraw_all
from .modules.modules import (
    reload_addon,
    unregister_module,
)
from ....lib.utils.node_tree.scripting_node_trees import has_addon
from .generator import generate_addon, has_changes
import bpy


def watch_changes():
    module_name = bpy.context.scene.sna.addon.module_name

    if has_changes() and has_addon():
        if bpy.context.scene.sna.addon.enabled:
            files_changed = generate_addon()
            if files_changed:
                reload_addon(module_name)
        else:
            unregister_module(module_name)
        redraw_all()

    if bpy.context.scene.sna.addon.force_production:
        return 2
    elif has_addon() or not bpy.context.scene.sna.addon.enabled:
        return 0.25
    return 1
