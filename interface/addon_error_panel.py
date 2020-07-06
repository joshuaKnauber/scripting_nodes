import bpy
from textwrap import wrap
from ..compile.compiler import compiler
from ..handler.error_message_handler import ErrorMessageHandler


class SN_PT_ErrorLogPanel(bpy.types.Panel):
    """Creates a panel for displaying error messages in the node editors sidebar"""
    bl_label = "Errors"
    bl_order = 3
    bl_idname = "SN_PT_ErrorLogPanel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Visual Scripting"

    error_message_handler = ErrorMessageHandler()

    @classmethod
    def poll(cls, context):
        return bool(compiler().get_active_addons_errors())

    def draw_error(self, layout, error):
        box = layout.box()
        col = box.column(align=True)

        row = col.row()
        if error["node"]:
            row.operator("scripting_nodes.find_error_node",text="",emboss=False,icon="NODE").node_name = error["node"].name

        row.alert = self.error_message_handler.error_fatal(error["error"])
        row.label(text=self.error_message_handler.error_name(error["error"]))

        line_length = bpy.context.region.width // bpy.context.scene.sn_properties.line_width
        error_message = wrap(self.error_message_handler.error_message(error["error"]),line_length)

        for line in error_message:
            col.label(text=line)

    def draw_header(self,context):
        self.layout.prop(context.scene.sn_properties,"show_line_width",text="",icon="PREFERENCES",emboss=False)

    def draw(self, context):
        layout = self.layout
        errors = compiler().get_active_addons_errors()
        
        if context.scene.sn_properties.show_line_width:
            box = layout.box()
            box.prop(context.scene.sn_properties,"line_width",slider=True,text="Line breaks")

        column = layout.column(align=False)

        for error in errors:
            self.draw_error(column, error)