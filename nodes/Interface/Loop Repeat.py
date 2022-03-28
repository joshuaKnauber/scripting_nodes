import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_RepeatInterfaceNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RepeatInterfaceNode"
    bl_label = "Loop Repeat (Interface)"
    bl_width_default = 200
    node_color = "INTERFACE"
    
    @property
    def layout_type(self):
        return self.active_layout
    
    def on_create(self, context):
        self.add_interface_input()
        self.add_integer_input("Repetitions").default_value = 2
        self.add_interface_output("Repeat")
        self.add_interface_output("Continue")
        self.add_integer_output("Step")
        
    def on_link_insert(self, from_socket, to_socket, is_output):
        if to_socket == self.inputs[0]:
            for out in self.outputs:
                if out.bl_label == "Interface":
                    for socket in out.to_sockets():
                        socket.node._evaluate(bpy.context)

    def evaluate(self, context):
        self.outputs["Step"].python_value = f"i_{self.static_uid}"
        self.code = f"""
                    for i_{self.static_uid} in range({self.inputs['Repetitions'].python_value}):
                        {self.indent(self.outputs['Repeat'].python_value, 6) if self.outputs['Repeat'].python_value.strip() else 'pass'}
                    {self.indent(self.outputs['Continue'].python_value, 5)}
                    """