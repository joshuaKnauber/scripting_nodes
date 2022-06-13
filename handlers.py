import bpy
from bpy.app.handlers import persistent
from . import bl_info
from .nodes.compiler import compile_addon, unregister_addon
from .settings.updates import check_serpens_updates
from .settings.easybpy import check_easy_bpy_install
from .settings.handle_script_changes import unwatch_script_changes, watch_script_changes, update_script_nodes
from .extensions.snippet_ops import load_snippets
from .msgbus import subscribe_to_name_change



@persistent
def depsgraph_handler(dummy):
    for group in bpy.data.node_groups:
        if group.bl_idname == "ScriptingNodesTree":
            group.use_fake_user = True
            # add empty collection for node drawing
            if not "empty" in group.node_refs:
                group.node_refs.add().name = "empty"



@persistent
def load_handler(dummy):
    bpy.context.scene.sn.picker_active = False
    subscribe_to_name_change()
    check_easy_bpy_install()
    if bpy.context.scene.sn.compile_on_load:
        compile_addon()
    check_serpens_updates(bl_info["version"])
    bpy.ops.sn.reload_packages()
    load_snippets()
    bpy.context.scene.sn.hide_preferences = False
    unwatch_script_changes()
    if bpy.context.scene.sn.watch_script_changes:
        watch_script_changes()



@persistent
def unload_handler(dummy=None):
    unwatch_script_changes()
    unregister_addon()



@persistent
def undo_post(dummy=None):
    if hasattr(bpy.context, "space_data") and hasattr(bpy.context.space_data, "node_tree"):
        ntree = bpy.context.space_data.node_tree
        if ntree.bl_idname == "ScriptingNodesTree":
            compile_addon()
            
            
            
@persistent
def save_pre(dummy=None):
    if bpy.context.scene.sn.watch_script_changes:
        update_script_nodes(True)