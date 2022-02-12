import bpy
from bpy.app.handlers import persistent
from . import bl_info
from .settings.updates import check_serpens_updates
from .node_tree.graphs.node_tree import compile_all, unregister_all
from .settings.easybpy import check_easy_bpy_install
from .msgbus import subscribe_to_name_change



@persistent
def depsgraph_handler(dummy):
    for group in bpy.data.node_groups:
        if group.bl_idname == "ScriptingNodesTree":
            group.use_fake_user = True



@persistent
def load_handler(dummy):
    subscribe_to_name_change()
    check_easy_bpy_install()
    if bpy.context.scene.sn.compile_on_load:
        compile_all()
    check_serpens_updates(bl_info["version"])
    bpy.ops.sn.reload_packages()
    bpy.context.scene.sn.hide_preferences = False



@persistent
def unload_handler(dummy=None):
    unregister_all()



@persistent
def undo_post(dummy=None):
    if hasattr(bpy.context, "space_data") and hasattr(bpy.context.space_data, "node_tree"):
        ntree = bpy.context.space_data.node_tree
        if ntree.bl_idname == "ScriptingNodesTree":
            unregister_all()
            compile_all(True)