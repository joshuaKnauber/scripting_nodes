from scripting_nodes.src.features.node_tree.code_gen.file_management.clear_addon import (
    clear_module_files,
)
from scripting_nodes.src.features.node_tree.code_gen.modules.persisted import (
    add_module_to_persist,
    remove_module_to_persist,
)
from scripting_nodes.src.features.node_tree.code_gen.generator import generate_addon
import bpy
from bpy.app.handlers import persistent


@persistent
def on_save_pre(dummy):
    if bpy.context.scene.sna.addon.persist_addon:
        generate_addon(dev_module=False)
        add_module_to_persist(bpy.context.scene.sna.addon.module_name)
    else:
        clear_module_files(bpy.context.scene.sna.addon.module_name)
        remove_module_to_persist(bpy.context.scene.sna.addon.module_name)


def register():
    bpy.app.handlers.save_pre.append(on_save_pre)


def unregister():
    bpy.app.handlers.save_pre.remove(on_save_pre)
