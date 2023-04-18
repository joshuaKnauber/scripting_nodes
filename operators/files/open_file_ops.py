import bpy
import os
from ...properties.files.load_files import load_files


class SN_OT_OpenFileOps(bpy.types.Operator):
    bl_idname = "sn.open_file"
    bl_label = "Open File"
    bl_description = "Opens this file in an editor"

    path: bpy.props.StringProperty()

    def get_area(self, context, editor_type: str):
        for area in context.screen.areas:
            if area.type == editor_type:
                return area
        bpy.ops.screen.area_split(direction="VERTICAL", factor=0.5)
        new_area = context.screen.areas[-1]
        new_area.type = editor_type
        return new_area

    def open_text_file(self, context):
        area = self.get_area(context, "TEXT_EDITOR")
        for text in bpy.data.texts:
            if text.filepath == self.path:
                area.spaces.active.text = text
                break
        else:
            text = bpy.data.texts.load(self.path)
            area.spaces.active.text = text

    def open_blend_file(self, context):
        pass

    def open_image_file(self, context):
        area = self.get_area(context, "IMAGE_EDITOR")
        area.spaces.active.image = bpy.data.images.load(self.path, check_existing=True)

    def execute(self, context):
        filetype = self.path.split(".")[-1]
        if filetype in ["py", "txt", "json"]:
            self.open_text_file(context)
        elif filetype == "blend":
            self.open_blend_file(context)
        elif filetype in ["jpg", "png"]:
            self.open_image_file(context)
        return {"FINISHED"}
