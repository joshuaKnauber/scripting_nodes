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
        self.add_boolean_input("Enabled")["default_value"] = True
        self.add_boolean_input("Split Layout")
        self.add_boolean_input("Decorate Layout")
        self.add_factor_input("Scale X")["default_value"] = 1
        self.add_factor_input("Scale Y")["default_value"] = 1
        self.add_enum_input("Alignment")["items"] = str(["Expand", "Left", "Center", "Right"])
        self.add_interface_output()
        self.add_dynamic_interface_output()

    def evaluate(self, context):
        self.code = f"""
                    row = {self.active_layout}.row(heading={self.inputs["Label"].python_value}, align={self.inputs["Align"].python_value})
                    row.alert = {self.inputs["Alert"].python_value}
                    row.enabled = {self.inputs["Enabled"].python_value}
                    row.use_property_split = {self.inputs["Split Layout"].python_value}
                    row.use_property_decorate = {self.inputs["Decorate Layout"].python_value}
                    row.scale_x = {self.inputs["Scale X"].python_value}
                    row.scale_y = {self.inputs["Scale Y"].python_value}
                    row.alignment = {self.inputs["Alignment"].python_value}.upper()
                    {self.indent([out.python_value for out in self.outputs[:-1]], 5)}
                    """
