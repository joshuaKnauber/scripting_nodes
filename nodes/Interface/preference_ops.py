import bpy



class SN_OT_OpenPreferences(bpy.types.Operator):
    bl_idname = "sn.open_preferences"
    bl_label = "Open Preferences"
    bl_description = "Open Preferences"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.screen.userpref_show("INVOKE_DEFAULT")
        context.preferences.active_section = "ADDONS"
        context.window_manager.addon_search = "Serpens"
        bpy.ops.preferences.addon_expand(module="blender_visual_scripting_addon")
        return {"FINISHED"}
