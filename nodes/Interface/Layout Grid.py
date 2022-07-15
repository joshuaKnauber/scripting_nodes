import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_LayoutGridNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_LayoutGridNode"
    bl_label = "Grid"
    bl_width_default = 200
    node_color = "INTERFACE"
    
    def layout_type(self, socket):
        if socket.name == "Grid":
            return f"grid_{self.static_uid}"
        return self.active_layout

    def on_create(self, context):
        self.add_interface_input()
        self.add_integer_input("Columns").default_value = 6
        self.add_boolean_input("Fill Row By Row").default_value = False
        self.add_boolean_input("Even Columns").default_value = False
        self.add_boolean_input("Even Rows").default_value = False
        self.add_boolean_input("Align")
        self.add_boolean_input("Enabled")["default_value"] = True
        self.add_boolean_input("Active")["default_value"] = True
        self.add_boolean_input("Split Layout")
        self.add_boolean_input("Decorate Layout")
        self.add_boolean_input("Use Invoke")["default_value"] = True
        self.add_float_input("Scale X")["default_value"] = 1
        self.add_float_input("Scale Y")["default_value"] = 1
        self.add_enum_input("Alignment")["items"] = str(["Expand", "Left", "Center", "Right"])
        self.add_dynamic_interface_output("Grid")

    def evaluate(self, context):
        self.code = f"""
                    grid_{self.static_uid} = {self.active_layout}.grid_flow(columns={self.inputs["Columns"].python_value}, row_major={self.inputs["Fill Row By Row"].python_value}, even_columns={self.inputs["Even Columns"].python_value}, even_rows={self.inputs["Even Rows"].python_value}, align={self.inputs["Align"].python_value})
                    grid_{self.static_uid}.enabled = {self.inputs["Enabled"].python_value}
                    {f"grid_{self.static_uid}.active = {self.inputs['Active'].python_value}" if "Active" in self.inputs else ""}
                    grid_{self.static_uid}.use_property_split = {self.inputs["Split Layout"].python_value}
                    grid_{self.static_uid}.use_property_decorate = {self.inputs["Decorate Layout"].python_value}
                    grid_{self.static_uid}.alignment = {self.inputs["Alignment"].python_value}.upper()
                    grid_{self.static_uid}.scale_x = {self.inputs["Scale X"].python_value}
                    grid_{self.static_uid}.scale_y = {self.inputs["Scale Y"].python_value}
                    grid_{self.static_uid}.operator_context = "INVOKE_DEFAULT" if {"False" if not "Use Invoke" in self.inputs else self.inputs["Use Invoke"].python_value} else "EXEC_DEFAULT"
                    {self.indent([out.python_value if out.name == 'Grid' else '' for out in self.outputs], 5)}
                    """
