import bpy
import os
from ...properties.files.update_file import update_file


class SN_OT_CreateFolder(bpy.types.Operator):
    bl_idname = "sn.create_folder"
    bl_label = "Create Folder"
    bl_description = "Creates a new folder at the selected location"

    path: bpy.props.StringProperty(options={"SKIP_SAVE"})

    def execute(self, context):
        path = self.path
        if os.path.isfile(path):
            path = os.path.dirname(path)

        if os.path.exists(path):
            new_dir_name = os.path.join(path, "New Folder")
            count = 0
            while os.path.exists(new_dir_name):
                count += 1
                new_dir_name = os.path.join(path, f"New Folder {count}")
            os.mkdir(new_dir_name)
            update_file("", new_dir_name)
        return {"FINISHED"}
