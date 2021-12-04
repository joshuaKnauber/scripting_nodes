import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_LayoutRowNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_LayoutRowNode"
    bl_label = "Row"
    layout_type = "row"
    bl_width_default = 200
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_interface_input()
        self.add_string_input("Label")
        self.add_boolean_input("Align")
        self.add_boolean_input("Alert")
        self.add_boolean_input("Enabled")
        self.add_boolean_input("Split Layout")
        self.add_boolean_input("Decorate Layout")
        self.add_boolean_input("Scale X")
        self.add_boolean_input("Scale Y")
        # self.add_enum_input("Alignment").items = str(["Expand", "Left", "Center", "Right"])
        self.add_interface_output()
        self.add_dynamic_interface_output()

    def evaluate(self, context):
                    # row.alignment = {self.inputs["Alignment"].python_value}.upper()
        self.code = f"""
                    row = {self.active_layout}.row()
                    {self.indent([out.python_value for out in self.outputs[:-1]], 5)}
                    """

    def draw_node(self, context, layout):
        pass