from xml.dom.minidom import Element
import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.VariableReferenceNode import VariableReferenceNode



class SN_RemoveFromListNode(bpy.types.Node, SN_ScriptingBaseNode, VariableReferenceNode):

    bl_idname = "SN_RemoveFromListNode"
    bl_label = "Remove From List"
    node_color = "PROPERTY"


    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.add_data_input("Element")
        self.var_ntree = self.node_tree
                
    def update_method(self, context):
        if self.method == "INDEX":
            self.convert_socket(self.inputs[1], self.socket_names["Integer"])
            self.inputs[1].name = "Index"
        else:
            self.convert_socket(self.inputs[1], self.socket_names["Data"])
            self.inputs[1].name = "Element"
        self._evaluate(context)
        
    method: bpy.props.EnumProperty(name="Method",
                            description="How to find the element to delete",
                            items=[("ELEMENT", "Element", "Use the elements value to delete it"),
                                   ("INDEX", "Index", "Use the elements index to delete it")],
                            update=update_method)


    def evaluate(self, context):
        method = "pop" if self.method == "INDEX" else "remove"

        var = self.get_var()
        if var and var.variable_type == "List":
            self.code = f"""
                        {var.data_path}.{method}({self.inputs[1].python_value})
                        {self.indent(self.outputs[0].python_value, 6)}
                        """
        else:
            self.code = f"""
                        {self.indent(self.outputs[0].python_value, 6)}
                        """


    def draw_node(self, context, layout):
        self.draw_variable_reference(layout)
        var = self.get_var()
        if var and not var.variable_type == "List":
            row = layout.row()
            row.alert = True
            row.label(text="Not a list variable!", icon="ERROR")
        elif var:
            layout.prop(self, "method", expand=True)