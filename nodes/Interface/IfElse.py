import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_IfElseInterfaceNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IfElseInterfaceNode"
    bl_label = "If/Else Interface"
    bl_width_default = 200
    node_color = "INTERFACE"
    layout_type = "layout"
    
    def on_create(self, context):
        self.add_interface_input()
        self.add_boolean_input("Condition").default_value = True
        self.add_interface_output("Continue")
        self.add_interface_output("True")
        self.add_interface_output("False")
        
    def on_link_insert(self, from_socket, to_socket, is_output):
        if to_socket == self.inputs[0]:
            self.layout_type = self.active_layout

    def evaluate(self, context):
        self.code = f"""
                    if {self.inputs['Condition'].python_value}:
                        {self.outputs['True'].python_value if self.outputs['True'].python_value.strip() else 'pass'}
                    else:
                        {self.outputs['False'].python_value if self.outputs['False'].python_value.strip() else 'pass'}
                    {self.outputs['Continue'].python_value}
                    """