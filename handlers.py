import bpy
from bpy.app.handlers import persistent
from . import bl_info
from .settings.updates import check_serpens_updates



@persistent
def depsgraph_handler(dummy):
    for group in bpy.data.node_groups:
        if group.bl_idname == "ScriptingNodesTree":
            group.use_fake_user = True


@persistent
def load_handler(dummy):
    check_serpens_updates(bl_info["version"])


@persistent
def unload_handler(dummy=None):
    pass