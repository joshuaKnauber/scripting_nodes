import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_LayoutBoxNodeNew(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_LayoutBoxNodeNew"
    bl_label = "Box"
    bl_width_default = 200
    node_color = "INTERFACE"
    
    def layout_type(self, socket):
        if socket.name == "Box":
            return f"box_{self.static_uid}"
        return self.active_layout

    def on_create(self, context):
        self.add_interface_input()
        self.add_boolean_input("Alert")
        self.add_boolean_input("Enabled")["default_value"] = True
        self.add_boolean_input("Active")["default_value"] = True
        self.add_boolean_input("Split Layout")
        self.add_boolean_input("Decorate Layout")
        self.add_float_input("Scale X")["default_value"] = 1
        self.add_float_input("Scale Y")["default_value"] = 1
        self.add_enum_input("Alignment")["items"] = str(["Expand", "Left", "Center", "Right"])
        self.add_dynamic_interface_output("Box")
        self.add_dynamic_interface_output("Interface").passthrough_layout_type = True

    def evaluate(self, context):
        self.code = f"""
                    box_{self.static_uid} = {self.active_layout}.box()
                    box_{self.static_uid}.alert = {self.inputs["Alert"].python_value}
                    box_{self.static_uid}.enabled = {self.inputs["Enabled"].python_value}
                    {f"box_{self.static_uid}.active = {self.inputs['Active'].python_value}" if "Active" in self.inputs else ""}
                    box_{self.static_uid}.use_property_split = {self.inputs["Split Layout"].python_value}
                    box_{self.static_uid}.use_property_decorate = {self.inputs["Decorate Layout"].python_value}
                    box_{self.static_uid}.alignment = {self.inputs["Alignment"].python_value}.upper()
                    box_{self.static_uid}.scale_x = {self.inputs["Scale X"].python_value}
                    box_{self.static_uid}.scale_y = {self.inputs["Scale Y"].python_value}
                    {self.indent([out.python_value if out.name == 'Box' else '' for out in self.outputs], 5)}
                    {self.indent([out.python_value if out.name == 'Interface' else '' for out in self.outputs], 5)}
                    """
