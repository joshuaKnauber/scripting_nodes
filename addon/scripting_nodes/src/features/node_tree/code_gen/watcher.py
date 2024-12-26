from .modules.to_remove import add_module_to_remove
from .modules.modules import (
    reload_addon,
    unregister_last_module,
)
from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import has_addon
from .generator import generate_addon
import bpy


# persist addon -> dont remove module & build prod on save?


def watch_changes():
    is_dev = not bpy.context.scene.sna.addon.force_production

    if bpy.context.scene.sna.addon.enabled:
        module, has_changes = generate_addon(is_dev)
        if module and has_changes:
            add_module_to_remove(module)
            reload_addon(module)
    else:
        unregister_last_module()

    if bpy.context.scene.sna.addon.force_production:
        return 2
    elif has_addon():
        return 0.25
    return 1
