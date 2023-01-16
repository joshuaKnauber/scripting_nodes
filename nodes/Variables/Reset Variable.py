import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.VariableReferenceNode import VariableReferenceNode



class SN_ResetVariableNode(SN_ScriptingBaseNode, bpy.types.Node, VariableReferenceNode):

    bl_idname = "SN_ResetVariableNode"
    bl_label = "Reset Variable"
    node_color = "PROPERTY"


    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.ref_ntree = self.node_tree


    def evaluate(self, context):
        var = self.get_var()
        if var:
            self.code = f"""
                        {var.data_path} = {var.var_default}
                        {self.indent(self.outputs[0].python_value, 6)}
                        """
                
        else:
            self.code = f"""
                        {self.indent(self.outputs[0].python_value, 6)}
                        """


    def draw_node(self, context, layout):
        self.draw_variable_reference(layout)