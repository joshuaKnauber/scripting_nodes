import bpy
from bpy.app.handlers import persistent
from . import bl_info
from .settings.updates import check_serpens_updates
from .node_tree.graphs.node_tree import compile_all, unregister_all
from .settings.easybpy import check_easy_bpy_install



@persistent
def depsgraph_handler(dummy):
    for group in bpy.data.node_groups:
        if group.bl_idname == "ScriptingNodesTree":
            group.use_fake_user = True



@persistent
def load_handler(dummy):
    check_easy_bpy_install()
    if bpy.context.scene.sn.compile_on_load:
        compile_all()
    check_serpens_updates(bl_info["version"])



@persistent
def unload_handler(dummy=None):
    unregister_all()