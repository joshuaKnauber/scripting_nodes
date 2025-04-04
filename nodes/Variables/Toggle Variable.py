import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.VariableReferenceNode import VariableReferenceNode



class SN_ToggleVariableNode(SN_ScriptingBaseNode, bpy.types.Node, VariableReferenceNode):

    bl_idname = "SN_ToggleVariableNode"
    bl_label = "Toggle Variable"
    node_color = "PROPERTY"
        

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.ref_ntree = self.node_tree


    def evaluate(self, context):
        var = self.get_var()
        if var:
            if var.variable_type != "Boolean":
                self.code = f"""
                            {self.indent(self.outputs[0].python_value, 7)}
                            """
            else:
                self.code = f"""
                            {var.data_path} = not {var.data_path}
                            {self.indent(self.outputs[0].python_value, 7)}
                            """
        else:
            self.code = f"""
                        {self.indent(self.outputs[0].python_value, 6)}
                        """


    def draw_node(self, context, layout):
        self.draw_variable_reference(layout)
        var = self.get_var()
        if var and not var.variable_type == "Boolean":
            row = layout.row()
            row.alert = True
            row.label(text="Not a boolean variable!", icon="ERROR")