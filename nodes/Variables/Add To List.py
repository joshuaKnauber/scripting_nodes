import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.VariableReferenceNode import VariableReferenceNode



class SN_AddToListNode(bpy.types.Node, SN_ScriptingBaseNode, VariableReferenceNode):

    bl_idname = "SN_AddToListNode"
    bl_label = "Add To List"
    node_color = "PROPERTY"
        

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.add_data_input("Item")
        self.add_integer_input("Index").set_hide(True)
        self.add_list_input("List").set_hide(True)
        self.var_ntree = self.node_tree
        
        
    def update_method(self, context):
        self.inputs["Index"].set_hide(self.method != "Insert")
        self._evaluate(context)
        
    method: bpy.props.EnumProperty(name="Method",
                            description="Method to add the item to the list",
                            items=[("Append", "Append", "Append"),
                                   ("Prepend", "Prepend", "Prepend"),
                                   ("Insert", "Insert", "Insert")],
                            update=update_method)


    def evaluate(self, context):
        var = self.get_var()
        if var:
            if self.method == "Append":
                self.code = f"""
                            {var.data_path}.append({self.inputs[1].python_value})
                            {self.indent(self.outputs[0].python_value, 7)}
                            """
            elif self.method == "Prepend":
                self.code = f"""
                            {var.data_path}.insert(0, {self.inputs[1].python_value})
                            {self.indent(self.outputs[0].python_value, 7)}
                            """
            elif self.method == "Insert":
                self.code = f"""
                            {var.data_path}.insert({self.inputs['Index'].python_value}, {self.inputs[1].python_value})
                            {self.indent(self.outputs[0].python_value, 7)}
                            """


    def draw_node(self, context, layout):
        self.draw_variable_reference(layout)
        var = self.get_var()
        if var and not var.variable_type == "List":
            row = layout.row()
            row.alert = True
            row.label(text="Not a list variable!", icon="ERROR")
        layout.prop(self, "method")