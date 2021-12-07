import bpy
import os


class SN_OT_ClearConsole(bpy.types.Operator):
    bl_idname = "sn.clear_console"
    bl_label = "Clear System Console"
    bl_description = "This operator clears the system console."
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        if os.name == "nt":
            os.system("cls") 
        else:
            os.system("clear") 
        return {"FINISHED"}