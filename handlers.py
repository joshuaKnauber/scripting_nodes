import bpy
from bpy.app.handlers import persistent



@persistent
def depsgraph_handler(dummy):
    for group in bpy.data.node_groups:
        if group.bl_idname == "ScriptingNodesTree":
            group.use_fake_user = True


@persistent
def load_handler(dummy):
    pass


@persistent
def unload_handler(dummy=None):
    pass