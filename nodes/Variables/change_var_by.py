import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup


class SN_ChangeVariableNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ChangeVariableNode"
    bl_label = "Change Variable By"
    # bl_icon = "GRAPH"
    bl_width_default = 180

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

            if var.var_type in ["BOOLEAN", "LIST"]:
                if len(self.inputs) > 1:
                    self.inputs.remove(self.inputs[1])

            if not len(self.inputs) > 1:
                if var.var_type == "STRING":
                    self.add_string_input("")
                elif var.var_type == "INTEGER":
                    self.add_integer_input("")
                elif var.var_type == "FLOAT":
                    self.add_float_input("")
            
            if len(self.inputs) > 1:
                idname = {"STRING": "SN_StringSocket", "INTEGER": "SN_IntegerSocket", "FLOAT": "SN_FloatSocket"}
                if idname[var.var_type] != self.inputs[1].bl_idname:
                    self.change_socket_type(self.inputs[1], idname[var.var_type])


    def on_node_update(self):
        if not len(self.inputs) > 1:
            self.update_search(bpy.context)

    add_sub: bpy.props.EnumProperty(items=[("+=", "Add", "Add to the variable"), ("-=", "Subtract", "Subtract from the variable")], name="Operation")


    def on_create(self, context):
        self.add_execute_input("Change Variable by")
        self.add_execute_output("Execute")


    search_value: bpy.props.StringProperty(update=update_search)
    identifier: bpy.props.StringProperty()


    def draw_node(self,context,layout):
        layout.prop_search(self, "search_value", self.node_tree, "sn_variables", text="")

        if self.search_value != "" and not self.search_value in self.node_tree.sn_variables:
            if len(self.inputs) > 1:
                self.inputs.remove(self.inputs[1])

        if self.search_value in self.node_tree.sn_variables:
            if self.node_tree.sn_variables[self.search_value].var_type in ["INTEGER", "FLOAT"]:
                layout.prop(self, "add_sub", expand=True)

            if self.node_tree.sn_variables[self.search_value].var_type in ["BOOLEAN", "LIST"]:
                if len(self.inputs) > 1:
                    self.inputs.remove(self.inputs[1])
                layout.label(text="Please use a set variable node!")


    def code_evaluate(self, context, touched_socket):
        if len(self.inputs) < 2:
            if self.search_value != "":
                self.add_error("Wrong variable", "Wrong variable selected")
            else:
                self.add_error("No variable", "No variable selected")

            return {
                "code": f"""
                        {self.outputs[0].code(6)}
                        """
            }

        else:
            if self.node_tree.sn_variables[self.search_value].var_type == "STRING":
                self.add_sub = "+="

            return {
                "code": f"""
                        {self.get_python_name(self.node_tree.name)}["{self.node_tree.sn_variables[self.search_value].identifier}"] {self.add_sub} {self.inputs[1].code()}
                        {self.outputs[0].code(6)}
                        """
            }
