import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.VariableReferenceNode import VariableReferenceNode



class SN_SetVariableNode(bpy.types.Node, SN_ScriptingBaseNode, VariableReferenceNode):

    bl_idname = "SN_SetVariableNode"
    bl_label = "Set Variable"
    node_color = "PROPERTY"
        

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.add_data_input("Value")
        self.var_ntree = self.node_tree
        
        
    def on_var_changed(self):
        var = self.get_var()
        if var:
            self.convert_socket(self.inputs[1], self.socket_names[var.variable_type])
        else:
            self.convert_socket(self.inputs[1], self.socket_names["Data"])


    def evaluate(self, context):
        var = self.get_var()
        if var:
            self.code = f"""
                        {var.data_path} = {self.inputs[1].python_value}
                        {self.indent(self.outputs[0].python_value, 6)}
                        """
        else:
            self.code = f"""
                        {self.indent(self.outputs[0].python_value, 6)}
                        """


    def draw_node(self, context, layout):
        self.draw_variable_reference(layout)