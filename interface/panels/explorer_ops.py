import bpy
import subprocess



class SN_OT_OpenExplorer(bpy.types.Operator):
    bl_idname = "sn.open_explorer"
    bl_label = "Open Explorer"
    bl_description = "Open the explorer"
    bl_options = {"REGISTER", "INTERNAL"}

    path: bpy.props.StringProperty({"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        subprocess.Popen(f'explorer /select,"{self.path}"')
        return {"FINISHED"}