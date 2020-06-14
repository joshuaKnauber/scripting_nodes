import bpy
from ..compile.compiler import compiler


class SN_OT_CompileActive(bpy.types.Operator):
    bl_idname = "scripting_nodes.compile_active"
    bl_label = "Reload Addon"
    bl_description = "Reloads the active node trees addon"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        compiler().compile_active()
        return {"FINISHED"}
