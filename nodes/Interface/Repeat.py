import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_RepeatInterfaceNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RepeatInterfaceNode"
    bl_label = "Repeat Interface"
    bl_width_default = 200
    node_color = "INTERFACE"
    layout_type = "layout"
    
    def on_create(self, context):
        self.add_interface_input()
        self.add_integer_input("Repetitions").default_value = 2
        self.add_interface_output("Repeat")
        self.add_interface_output("Continue")
        self.add_integer_output("Step")
        
    def on_link_insert(self, from_socket, to_socket, is_output):
        if to_socket == self.inputs[0]:
            self.layout_type = self.active_layout

    def evaluate(self, context):
        self.outputs["Step"].python_value = f"i_{self.static_uid}"
        self.code = f"""
                    for i_{self.static_uid} in range({self.inputs['Repetitions'].python_value}):
                        {self.indent(self.outputs['Repeat'].python_value, 6) if self.outputs['Repeat'].python_value.strip() else 'pass'}
                    {self.indent(self.outputs['Continue'].python_value, 5)}
                    """