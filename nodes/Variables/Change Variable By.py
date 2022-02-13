import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.VariableReferenceNode import VariableReferenceNode



class SN_ChangeVariableByNode(bpy.types.Node, SN_ScriptingBaseNode, VariableReferenceNode):

    bl_idname = "SN_ChangeVariableByNode"
    bl_label = "Change Variable By"
    node_color = "PROPERTY"
        

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.add_data_input("Change By")
        self.var_ntree = self.node_tree

    operation: bpy.props.EnumProperty(items=[("+=", "Add", "Add to variable value"),
                                            ("-=", "Subtract", "Subtract from variable value")],
                                    name="Operation",
                                    description="Operation to perform with the input data",
                                    update=SN_ScriptingBaseNode._evaluate)

    def on_var_changed(self):
        var = self.get_var()
        if var and var.variable_type in ["String", "Integer", "Float"]:
            if var.variable_type == "String":
                self.operation = "+="
            self.convert_socket(self.inputs[1], self.socket_names[var.variable_type])
        else:
            self.convert_socket(self.inputs[1], self.socket_names["Data"])


    def evaluate(self, context):
        var = self.get_var()
        if var:
            if not var.variable_type in ["String", "Integer", "Float"]:
                self.code = f"""
                            {self.indent(self.outputs[0].python_value, 7)}
                            """
            else:
                self.code = f"""
                            {var.data_path} {self.operation} {self.inputs[1].python_value}
                            {self.indent(self.outputs[0].python_value, 7)}
                            """
        else:
            self.code = f"""
                        {self.indent(self.outputs[0].python_value, 6)}
                        """


    def draw_node(self, context, layout):
        self.draw_variable_reference(layout)

        var = self.get_var()
        if var and var.variable_type in ["Integer", "Float"]:
            layout.prop(self, "operation", expand=True)

        if var and not var.variable_type in ["String", "Integer", "Float"]:
            row = layout.row()
            row.alert = True
            row.label(text="Not a string, integer or float variable!", icon="ERROR")