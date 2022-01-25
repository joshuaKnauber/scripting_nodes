import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_IfElseInterfaceNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IfElseInterfaceNode"
    bl_label = "If/Else Interface"
    bl_width_default = 200
    
    type_default = "Interface"

    def on_create(self, context):
        self.add_execute_input()
        self.add_boolean_input("Condition")
        self.add_execute_output("Continue")
        self.add_execute_output("True")
        self.add_execute_output("False")
        
    def update_program_type(self, context):
        self.disable_evaluation = True
        self.convert_socket(self.inputs[0], self.socket_names[self.program_type])
        self.convert_socket(self.outputs[0], self.socket_names[self.program_type])
        self.convert_socket(self.outputs[1], self.socket_names[self.program_type])
        self.convert_socket(self.outputs[2], self.socket_names[self.program_type])
        if not self.label or self.label == "Interface" or self.label == "Execute":
            self.label = self.program_type
        self.disable_evaluation = False
        self._evaluate(context)
        
    program_type: bpy.props.EnumProperty(name="Type",
                                    description="Socket Type",
                                    items=[("Execute", "Execute", "Execute"),
                                           ("Interface", "Interface", "Interface")],
                                    default=type_default,
                                    update=update_program_type)

    def evaluate(self, context):
        self.code = f"""
                    if {self.inputs['Condition'].python_value}:
                        {self.outputs['True'].python_value if self.outputs['True'].python_value.strip() else 'pass'}
                    else:
                        {self.outputs['False'].python_value if self.outputs['True'].python_value.strip() else 'pass'}
                    {self.outputs['Continue'].python_value}
                    """
    
    def draw_node(self, context, layout):
        layout.prop(self, "program_type")