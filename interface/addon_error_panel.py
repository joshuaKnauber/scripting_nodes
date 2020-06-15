import bpy
from ..compile.compiler import compiler


class SN_PT_ErrorLogPanel(bpy.types.Panel):
    """Creates a panel for displaying error messages in the node editors sidebar"""
    bl_label = "Errors"
    bl_order = 2
    bl_idname = "SN_PT_ErrorLogPanel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Visual Scripting"

    @classmethod
    def poll(cls, context):
        return bool(compiler().get_active_addons_errors())

    def draw_error(self, layout, error_type, error_message, fatal, node):
        box = layout.box()
        col = box.column(align=True)

        row = col.row()
        if node != "":
            row.operator("scripting_nodes.find_error_node",text="",emboss=False,icon="NODE").node_name = node

        row.alert = fatal
        row.label(text=error_type)

        line_length = bpy.context.region.width // sn_props().line_width
        error_message = wrap(error_message,line_length)

        for line in error_message:
            col.label(text=line)

    def draw_header(self,context):
        pass#self.layout.prop(sn_props(),"show_line_width",text="",icon="PREFERENCES",emboss=False)

    def draw(self, context):
        layout = self.layout
        errors = compiler().get_active_addons_errors()
        for error in errors:
            layout.label(text=error["error"])
        """
        if sn_props().show_line_width:
            box = layout.box()
            box.prop(sn_props(),"line_width",slider=True,text="Line breaks")

        column = layout.column(align=False)

        if len(error_props()) > 0:
            for error in error_props():
                if error.fatal_error:
                    self.draw_error(column, error.error_type, error.error_message, True, error.node)
            for error in error_props():
                if not error.fatal_error:
                    self.draw_error(column, error.error_type, error.error_message, False, error.node)
        else:
            column.label(text="No errors found")
        """