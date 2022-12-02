import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_IfElseInterfaceNodeNew(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IfElseInterfaceNodeNew"
    bl_label = "If/Else (Interface)"
    bl_width_default = 200
    node_color = "INTERFACE"
    
    def on_create(self, context):
        self.add_interface_input()
        self.add_boolean_input("Condition").default_value = True
        self.add_interface_output("True").passthrough_layout_type = True
        self.add_interface_output("False").passthrough_layout_type = True
        self.add_interface_output("Interface").passthrough_layout_type = True

    def evaluate(self, context):
        self.code = f"""
                    if {self.inputs['Condition'].python_value}:
                        {self.indent(self.outputs['True'].python_value, 6) if self.outputs['True'].python_value.strip() else 'pass'}
                    {"else:" if self.outputs['False'].python_value.strip() else ""}
                        {self.indent(self.outputs['False'].python_value, 6) if self.outputs['False'].python_value.strip() else ''}
                    {self.indent(self.outputs['Interface'].python_value, 5)}
                    """