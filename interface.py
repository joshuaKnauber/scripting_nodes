import bpy
from .properties.property_utils import error_props


def node_tree_header(self, context):
    if context.space_data.tree_type == 'ScriptingNodesTree':
        layout = self.layout
        row = layout.row(align=True)
        row.scale_x = 1.3
        row.label(text="test")


class SN_PT_ErrorLogPanel(bpy.types.Panel):
    """Creates a panel for displaying error messages in the node editors sidebar"""
    bl_label = "Errors"
    bl_idname = "SN_PT_ErrorLogPanel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Scripting"

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ScriptingNodesTree'

    def get_line_length(self):
        char_width = 15
        return bpy.context.region.width // char_width

    def draw_error(self, layout, error_type, error_message):
        box = layout.box()

        box.label(text=error_type)

        line_length = self.get_line_length()
        error_message = [error_message[i:i+line_length] for i in range(0, len(error_message), line_length)]

        col = box.column(align=True)
        for line in error_message:
            col.label(text=line)

    def draw(self, context):
        layout = self.layout
        column = layout.column(align=False)

        for error in error_props():
            self.draw_error(column, error.error_type, error.error_message)
