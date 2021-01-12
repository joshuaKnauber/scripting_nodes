import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup


class SN_RemoveFromListNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RemoveFromListNode"
    bl_label = "Remove from List"
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

        self.update_search(bpy.context)

    def update_search(self, context):
        self.identifier = ""
        if not self.search_value in self.node_tree.sn_variables:
            self["search_value"] = ""
            if len(self.inputs) > 1:
                self.inputs.remove(self.inputs[1])

        else:
            var = self.node_tree.sn_variables[self.search_value]
            self.identifier = var.identifier

            if var.var_type == "LIST":
                if not len(self.inputs) > 1:
                    self.add_data_input("Value")
            else:
                if len(self.inputs) > 1:
                    self.inputs.remove(self.inputs[1])


    def on_create(self, context):
        self.add_execute_input("Remove from List")
        self.add_execute_output("Execute")


    search_value: bpy.props.StringProperty(update=update_search)
    identifier: bpy.props.StringProperty()


    def draw_node(self,context,layout):
        layout.prop_search(self, "search_value", self.node_tree, "sn_variables", text="")

        if self.search_value != "" and not self.search_value in self.node_tree.sn_variables:
            if len(self.inputs) > 1:
                self.inputs.remove(self.inputs[1])
        elif self.search_value != "" and self.node_tree.sn_variables[self.search_value].var_type != "LIST":
            layout.label(text="Please use a list variable!")
            if len(self.inputs) > 1:
                self.inputs.remove(self.inputs[1])


    def code_evaluate(self, context, touched_socket):
        if len(self.inputs) < 2:
            if self.search_value != "":
                self.add_error("Wrong variable", "You need to select a list variable selected")
            else:
                self.add_error("No variable", "No variable selected")

            return {
                "code": f"""
                        {self.outputs[0].code(6)}
                        """
            }

        else:
            return {
                "code": f"""
                        {self.get_python_name(self.node_tree.name)}["{self.node_tree.sn_variables[self.search_value].identifier}"].remove({self.inputs[1].code()})
                        {self.outputs[0].code(6)}
                        """
            }