import bpy
from .compiler import compile_tree

class SN_OT_ReloadButton(bpy.types.Operator):
    bl_idname = "scripting_nodes.compile"
    bl_label = "Reload"
    bl_description = "Compiles the Nodetree"
    bl_options = {"REGISTER","INTERNAL"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        compile_tree()
        return {"FINISHED"}
