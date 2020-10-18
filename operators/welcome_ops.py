import bpy


class SN_OT_WelcomeMessage(bpy.types.Operator):
    bl_idname = "scripting_nodes.welcome_message"
    bl_label = "Welcome!"
    bl_description = "Welcome Message"
    bl_options = {"REGISTER","INTERNAL"}

    def execute(self, context):
        context.preferences.addons[__name__.partition('.')[0]].preferences.tutorial_updated_self = True
        context.preferences.addons[__name__.partition('.')[0]].preferences.has_seen_tutorial = True
        bpy.ops.wm.save_userpref()
        return {"FINISHED"}

    def draw(self,context):
        self.layout.label(text="Thank you for using SERPENS!",icon="FUND")
        self.layout.separator()
        self.layout.label(text="If you haven't used the addon before,")
        self.layout.label(text="make sure to try the tutorial at the top right!")

    def invoke(self,context,event):
        return context.window_manager.invoke_props_dialog(self, width=300)



class SN_OT_UpdateeMessage(bpy.types.Operator):
    bl_idname = "scripting_nodes.update_message"
    bl_label = "There's an update for Serpens!"
    bl_description = ""
    bl_options = {"REGISTER","INTERNAL"}

    version: bpy.props.IntVectorProperty()

    def execute(self, context):
        return {"FINISHED"}

    def draw(self,context):
        self.layout.label(text="erpens - Visual Scripting", icon_value=bpy.context.scene.sn_icons[ "serpens" ].icon_id)
        self.layout.separator()
        self.layout.label(text="An update is available for you!")
        self.layout.label(text="You can download version "+str(self.version[0])+"."+str(self.version[1])+"."+str(self.version[2])+" right now!")
        self.layout.separator()
        self.layout.prop(bpy.context.preferences.addons[__name__.partition('.')[0]].preferences,"seen_new_update",text="Don't show again")

    def invoke(self,context,event):
        return context.window_manager.invoke_popup(self, width=300)