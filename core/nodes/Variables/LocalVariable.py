import bpy

from ....constants import sockets

from ..base_node import SNA_BaseNode


class SNA_NodeLocalVariable(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeLocalVariable"
    bl_label = "Local Variable"

    def on_create(self):
        self.add_input(sockets.PROGRAM)
        self.add_input(sockets.FLOAT, "Default")
        self.add_output(sockets.PROGRAM)
        self.add_output(sockets.FLOAT, "Value")

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        row = layout.row(align=True)
        # row.prop(self, "property_type", text="", icon_only=True)
        row.prop(self, "name", text="")

    def var_name(self):
        return f"var_{self.id}"

    def generate(self, context, trigger):
        self.code = f"""
            {self.var_name()} = 42
            {self.outputs["Program"].get_code(3)}
        """
        self.outputs["Value"].code = self.var_name()

        layout = self.inputs["Program"].get_meta("layout", "self.layout")
        self.outputs["Program"].set_meta("layout", layout)
