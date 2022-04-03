import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.VariableReferenceNode import VariableReferenceNode



class SN_GetVariableNode(bpy.types.Node, SN_ScriptingBaseNode, VariableReferenceNode):

    bl_idname = "SN_GetVariableNode"
    bl_label = "Get Variable"
    node_color = "PROPERTY"
        

    def on_create(self, context):
        self.add_data_output("Variable")
        self.ref_ntree = self.node_tree
        
        
    def on_var_changed(self):
        var = self.get_var()
        if var:
            self.convert_socket(self.outputs[0], self.socket_names[var.variable_type])
        else:
            self.convert_socket(self.outputs[0], self.socket_names["Data"])


    def evaluate(self, context):
        var = self.get_var()
        if var:
            self.outputs[0].python_value = var.data_path
        else:
            self.outputs[0].reset_value()


    def draw_node(self, context, layout):
        self.draw_variable_reference(layout)