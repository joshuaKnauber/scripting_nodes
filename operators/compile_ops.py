import bpy
from ..compile.compiler import compiler
from ..handler.error_handling import ErrorHandler


class SN_OT_CompileActive(bpy.types.Operator):
    bl_idname = "scripting_nodes.compile_active"
    bl_label = "Reload Addon"
    bl_description = "Reloads the active node trees addon"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        compiler().compile_active()
        return {"FINISHED"}


class SN_OT_UnregisterActive(bpy.types.Operator):
    bl_idname = "scripting_nodes.unregister_active"
    bl_label = "Unload Addon"
    bl_description = "Unloads the active node trees addon"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    @classmethod
    def poll(cls, context):
        return compiler().is_active_compiled()

    def execute(self, context):
        compiler().unregister_active()
        return {"FINISHED"}

class SN_OT_RunFunction(bpy.types.Operator):
    bl_idname = "scripting_nodes.run_function"
    bl_label = "Run Function"
    bl_description = "Runs a function"
    bl_options = {"REGISTER","INTERNAL"}

    ErrorHandler = ErrorHandler()
    funcName: bpy.props.StringProperty(name="Name", description="The name of the function")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.funcName != "":
            name = self.ErrorHandler.handle_text(self.funcName)
            compiler().run_function(name)
        return {"FINISHED"}