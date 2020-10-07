import bpy
from ..compile.compiler import compiler


class SN_OT_CompileActive(bpy.types.Operator):
    bl_idname = "scripting_nodes.compile_active"
    bl_label = "Compile Addon"
    bl_description = "Compiles the active node trees addon (Shift+R)"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    @classmethod
    def poll(cls, context):
        if hasattr(context.space_data,"node_tree"):
            if context.space_data.node_tree != None:
                return context.space_data.node_tree.bl_idname == "ScriptingNodesTree"
        return False

    def execute(self, context):
        success = compiler().compile_active()
        if success:
            has_fatal = False
            for error in compiler().get_active_addons_errors():
                if error["fatal"]:
                    has_fatal = True
            if not has_fatal:
                self.report({"INFO"},message="Successfully compiled addon!")
            else:
                self.report({"WARNING"},message="Fatal errors found! Check the N-Panel for debugging.")
        else:
            self.report({"ERROR"},message="Encountered a fatal error when compiling! Please contact the developers!")
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

class SN_OT_ClearPrints(bpy.types.Operator):
    bl_idname = "scripting_nodes.clear_prints"
    bl_label = "Clear Print Messages"
    bl_description = "Clears all print messages"
    bl_options = {"REGISTER","INTERNAL","UNDO"}

    def execute(self, context):
        context.scene.sn_properties.print_texts.clear()
        return {"FINISHED"}