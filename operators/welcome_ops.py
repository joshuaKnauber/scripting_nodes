import bpy


class SN_OT_WelcomeMessage(bpy.types.Operator):
    bl_idname = "scripting_nodes.welcome_message"
    bl_label = "Welcome!"
    bl_description = "Welcome Message"
    bl_options = {"REGISTER","INTERNAL"}

    def execute(self, context):
        context.preferences.addons[__name__.partition('.')[0]].preferences.has_seen_tutorial = True
        return {"FINISHED"}

    def draw(self,context):
        self.layout.label(text="Thank you for using SERPENS!",icon="FUND")
        self.layout.separator()
        self.layout.label(text="If you haven't used the addon before,")
        self.layout.label(text="make sure to try the tutorial at the top right!")

    def invoke(self,context,event):
        return context.window_manager.invoke_props_dialog(self, width=300)