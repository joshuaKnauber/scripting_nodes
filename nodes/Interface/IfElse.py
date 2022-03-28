import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_IfElseInterfaceNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IfElseInterfaceNode"
    bl_label = "If/Else (Interface)"
    bl_width_default = 200
    node_color = "INTERFACE"
    
    @property
    def layout_type(self):
        return self.active_layout
    
    def on_create(self, context):
        self.add_interface_input()
        self.add_boolean_input("Condition").default_value = True
        self.add_interface_output("True")
        self.add_interface_output("False")
        self.add_interface_output("Continue")
        
    def on_link_insert(self, from_socket, to_socket, is_output):
        if to_socket == self.inputs[0]:
            for out in self.outputs:
                if out.bl_label == "Interface":
                    for socket in out.to_sockets():
                        socket.node._evaluate(bpy.context)

    def evaluate(self, context):
        self.code = f"""
                    if {self.inputs['Condition'].python_value}:
                        {self.indent(self.outputs['True'].python_value, 6) if self.outputs['True'].python_value.strip() else 'pass'}
                    else:
                        {self.indent(self.outputs['False'].python_value, 6) if self.outputs['False'].python_value.strip() else 'pass'}
                    {self.indent(self.outputs['Continue'].python_value, 5)}
                    """