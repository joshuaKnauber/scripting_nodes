import bpy
import os
from bpy_extras.io_utils import ExportHelper
from ..compile.compiler import compiler


class SN_OT_ExportAddon(bpy.types.Operator):
    bl_idname = "scripting_nodes.export_addon"
    bl_label = "Export Addon"
    bl_description = "Exports the active node tree as a python file"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    filepath: bpy.props.StringProperty(name="File Path", description="Filepath used for exporting the file", maxlen=1024, subtype='FILE_PATH')

    filename_ext = ".py"
    filter_glob: bpy.props.StringProperty(default='*.py', options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        name = context.space_data.node_tree.addon_name.lower().replace(" ","_") + ".py"
        self.filepath = os.path.join(self.filepath,name)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        text = compiler().get_export_file()
        with open(self.filepath, "w") as addon_file:
            addon_file.write(text.as_string())
        bpy.data.texts.remove(text)
        return {"FINISHED"}
