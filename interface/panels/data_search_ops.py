import bpy



class SN_OT_ExitDataSearch(bpy.types.Operator):
    bl_idname = "sn.exit_search"
    bl_label = "Exit Data Search"
    bl_description = "Exits the data search mode"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        context.scene.sn.hide_preferences = False
        return {"FINISHED"}