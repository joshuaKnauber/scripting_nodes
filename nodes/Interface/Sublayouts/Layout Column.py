import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_LayoutColumnNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_LayoutColumnNodeNew"
    bl_label = "Column"
    bl_width_default = 200
    node_color = "INTERFACE"

    def layout_type(self, socket):
        if socket.name == "Column":
            return f"col_{self.static_uid}"
        return self.active_layout

    def on_create(self, context):
        self.add_interface_input()
        self.add_string_input("Label")
        self.add_boolean_input("Align")
        self.add_boolean_input("Alert")
        self.add_boolean_input("Enabled")["default_value"] = True
        self.add_boolean_input("Active")["default_value"] = True
        self.add_boolean_input("Split Layout")
        self.add_boolean_input("Decorate Layout")
        self.add_boolean_input("Use Invoke")["default_value"] = True
        self.add_float_input("Scale X")["default_value"] = 1
        self.add_float_input("Scale Y")["default_value"] = 1
        self.add_enum_input("Alignment")["items"] = str(
            ["Expand", "Left", "Center", "Right"]
        )
        self.add_dynamic_interface_output("Column")

    def evaluate(self, context):
        self.code = f"""
                    col_{self.static_uid} = {self.active_layout}.column(heading={self.inputs["Label"].python_value}, align={self.inputs["Align"].python_value})
                    col_{self.static_uid}.alert = {self.inputs["Alert"].python_value}
                    col_{self.static_uid}.enabled = {self.inputs["Enabled"].python_value}
                    {f"col_{self.static_uid}.active = {self.inputs['Active'].python_value}" if "Active" in self.inputs else ""}
                    col_{self.static_uid}.use_property_split = {self.inputs["Split Layout"].python_value}
                    col_{self.static_uid}.use_property_decorate = {self.inputs["Decorate Layout"].python_value}
                    col_{self.static_uid}.scale_x = {self.inputs["Scale X"].python_value}
                    col_{self.static_uid}.scale_y = {self.inputs["Scale Y"].python_value}
                    col_{self.static_uid}.alignment = {self.inputs["Alignment"].python_value}.upper()
                    col_{self.static_uid}.operator_context = "INVOKE_DEFAULT" if {self.inputs['Use Invoke'].python_value if 'Use Invoke' in self.inputs else 'True'} else "EXEC_DEFAULT"
                    {self.indent([out.python_value if out.name == 'Column' else '' for out in self.outputs], 5)}
                    """
