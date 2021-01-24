import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup


class SN_ResetVariableNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ResetVariableNode"
    bl_label = "Reset Variable"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def on_outside_update(self, node):
        for var in self.node_tree.sn_variables:
            if self.identifier:
                if var.identifier == self.identifier:
                    self.search_value = var.name

    def update_var(self, context):
        if self.search_value in self.node_tree.sn_variables:
            self.identifier = self.node_tree.sn_variables[self.search_value].identifier

        else:
            self.identifier = ""


    def on_create(self, context):
        self.add_execute_input("Set Variable")
        self.add_execute_output("Execute").mirror_name = True


    search_value: bpy.props.StringProperty(update=update_var)
    identifier: bpy.props.StringProperty()


    def draw_node(self,context,layout):
        layout.prop_search(self, "search_value", self.node_tree, "sn_variables", text="")


    def code_evaluate(self, context, touched_socket):
        if not self.search_value:
            self.add_error("No variable", "No variable selected")
            return {
                "code": f"""
                        {self.outputs[0].code(6)}
                        """
            }

        else:
            return {
                "code": f"""
                        {self.get_python_name(self.node_tree.name)}["{self.node_tree.sn_variables[self.search_value].identifier}"] = {self.node_tree.sn_variables[self.search_value].get_variable_default()}
                        {self.outputs[0].code(6)}
                        """
            }