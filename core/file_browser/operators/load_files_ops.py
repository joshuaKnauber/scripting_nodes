import bpy
from bpy_extras.io_utils import ImportHelper
import os
from ..load_files import load_files


class SN_OT_ConfirmLoad(bpy.types.Operator):
    bl_idname = "sn.confirm_load"
    bl_label = "Are you sure you want to load over 200 files from this folder?"
    bl_description = ""
    bl_options = {"REGISTER", "INTERNAL"}

    path: bpy.props.StringProperty()

    def execute(self, context):
        context.scene.sn.addon_location = self.path
        load_files(self.path)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class SN_OT_SelectLocation(bpy.types.Operator, ImportHelper):
    bl_idname = "sn.select_location"
    bl_label = "Select Location"
    bl_description = (
        "Lets you select an existing addon or a new folder to create the addon in"
    )

    filter_glob: bpy.props.StringProperty(
        default="",
        options={"HIDDEN"},
    )

    use_filter_folder: bpy.props.BoolProperty(
        default=True,
        options={"HIDDEN"},
    )

    def has_many_files(self, path):
        count = 0
        for _, dirs, files in os.walk(path):
            count += len(files)
            count += len(dirs)
            if count > 200:
                return True
        return False

    def execute(self, context):
        path = os.path.normpath(bpy.path.abspath(self.filepath))
        if os.path.isfile(path):
            path = os.path.dirname(path)

        if self.has_many_files(path):
            bpy.ops.sn.confirm_load("INVOKE_DEFAULT", path=path)
        else:
            context.scene.sn.addon_location = path
            load_files(path)
        return {"FINISHED"}

    def invoke(self, context, event):
        self.filepath = ""
        return super().invoke(context, event)
