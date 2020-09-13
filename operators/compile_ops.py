import bpy
from ..compile.compiler import compiler


class SN_OT_CompileActive(bpy.types.Operator):
    bl_idname = "scripting_nodes.compile_active"
    bl_label = "Compile Addon"
    bl_description = "Compiles the active node trees addon (Shift+R)"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    @classmethod
    def poll(cls, context):
        if context.space_data.node_tree != None:
            return context.space_data.node_tree.bl_idname == "ScriptingNodesTree"

    def execute(self, context):
        compiler().compile_active()
        self.report({"INFO"},message="Successfully compiled addon!")
        return {"FINISHED"}

    def draw(self,context):
        self.layout.label(text="You haven't changed your addons name yet:")
        self.layout.prop(context.space_data.node_tree, "addon_name", text="")
        self.layout.prop(context.space_data.node_tree, "ignore_name", text="Ignore Name")

    def invoke(self,context,event):
        if context.space_data.node_tree.addon_name == "New Addon" and not context.space_data.node_tree.ignore_name:
            return context.window_manager.invoke_props_dialog(self)
        return self.execute(context)


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

    funcName: bpy.props.StringProperty(name="Name", description="The name of the function")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.funcName != "":
            compiler().run_function(self.funcName)
        return {"FINISHED"}