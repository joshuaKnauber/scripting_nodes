import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_LayoutSplitNodeNew(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_LayoutSplitNodeNew"
    bl_label = "Split"
    bl_width_default = 200
    node_color = "INTERFACE"
    
    def layout_type(self, socket):
        if socket.name == "Split":
            return f"split_{self.static_uid}"
        return self.active_layout

    def on_create(self, context):
        self.add_interface_input()
        inp = self.add_float_input("Factor")
        inp.subtype = "FACTOR"
        inp.default_value = 0.5
        self.add_boolean_input("Align")
        self.add_boolean_input("Alert")
        self.add_boolean_input("Enabled")["default_value"] = True
        self.add_boolean_input("Active")["default_value"] = True
        self.add_boolean_input("Split Layout")
        self.add_boolean_input("Decorate Layout")
        self.add_boolean_input("Use Invoke")["default_value"] = True
        self.add_float_input("Scale X")["default_value"] = 1
        self.add_float_input("Scale Y")["default_value"] = 1
        self.add_enum_input("Alignment")["items"] = str(["Expand", "Left", "Center", "Right"])
        self.add_interface_output("Split")
        self.add_interface_output("Split")

    def evaluate(self, context):
        self.code = f"""
                    split_{self.static_uid} = {self.active_layout}.split(factor={self.inputs["Factor"].python_value}, align={self.inputs["Align"].python_value})
                    split_{self.static_uid}.alert = {self.inputs["Alert"].python_value}
                    split_{self.static_uid}.enabled = {self.inputs["Enabled"].python_value}
                    {f"split_{self.static_uid}.active = {self.inputs['Active'].python_value}" if "Active" in self.inputs else ""}
                    split_{self.static_uid}.use_property_split = {self.inputs["Split Layout"].python_value}
                    split_{self.static_uid}.use_property_decorate = {self.inputs["Decorate Layout"].python_value}
                    split_{self.static_uid}.scale_x = {self.inputs["Scale X"].python_value}
                    split_{self.static_uid}.scale_y = {self.inputs["Scale Y"].python_value}
                    split_{self.static_uid}.alignment = {self.inputs["Alignment"].python_value}.upper()
                    if not {self.inputs['Use Invoke'].python_value}: split_{self.static_uid}.operator_context = "EXEC_DEFAULT"
                    {self.indent(self.outputs[0].python_value, 5)}
                    {self.indent(self.outputs[1].python_value, 5)}
                    """
