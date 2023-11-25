import bpy

from ..base_node import SNA_BaseNode
from ....constants import sockets, variables


class SNA_NodeLocalVariable(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeLocalVariable"
    bl_label = "Local Variable"

    def update_type(self, context):
        self.convert_socket(
            self.inputs["Default"], sockets.VARIABLE_SOCKETS[self.variable_type]
        )
        self.convert_socket(
            self.outputs["Value"], sockets.VARIABLE_SOCKETS[self.variable_type]
        )
        self.mark_dirty()

    variable_type: bpy.props.EnumProperty(
        items=variables.variable_type_items,
        name="Type",
        description="Type of the data the variable stores",
        update=update_type,
    )

    def on_create(self):
        self.add_input(sockets.PROGRAM)
        self.add_input(sockets.FLOAT, "Default")
        self.add_output(sockets.PROGRAM)
        self.add_output(sockets.FLOAT, "Value")

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        row = layout.row(align=True)
        row.prop(self, "variable_type", text="", icon_only=True)
        row.prop(self, "name", text="")

    def var_name(self):
        return f"var_{self.id}"

    def generate(self, context, trigger):
        self.code = f"""
            {self.var_name()} = {self.inputs["Default"].get_code()}
            {self.outputs["Program"].get_code(3)}
        """
        self.outputs["Value"].code = self.var_name()

        layout = self.inputs["Program"].get_meta("layout", "self.layout")
        self.outputs["Program"].set_meta("layout", layout)
