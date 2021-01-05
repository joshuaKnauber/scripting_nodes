import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup


class SN_GetVariableNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetVariableNode"
    bl_label = "Get Variable"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def on_outside_update(self, node):
        for var in self.node_tree.sn_variables:
            if var.identifier == self.identifier:
                self.search_value = var.name
        
        self.update_search(bpy.context)

    def update_search(self, context):
        if not self.search_value in self.node_tree.sn_variables:
            self["search_value"] = ""
            self.outputs.clear()
            self.identifier = ""

        else:
            var = self.node_tree.sn_variables[self.search_value]
            self.identifier = var.identifier

            if not len(self.outputs):
                if var.var_type == "STRING":
                    self.add_string_output(var.name)
                elif var.var_type == "INTEGER":
                    self.add_integer_output(var.name)
                elif var.var_type == "FLOAT":
                    self.add_float_output(var.name)
                elif var.var_type == "BOOLEAN":
                    self.add_boolean_output(var.name)
                elif var.var_type == "LIST":
                    self.add_string_output(var.name)
            
            idname = {"STRING": "SN_StringSocket", "INTEGER": "SN_IntegerSocket", "FLOAT": "SN_FloatSocket", "BOOLEAN": "SN_BooleanSocket", "LIST": "SN_ExecuteSocket"}
            self.change_socket_type(self.outputs[0], idname[var.var_type])
            self.outputs[0].name = var.name


    def on_node_update(self):
        if not len(self.outputs):
            self.update_search(bpy.context)


    search_value: bpy.props.StringProperty(update=update_search)
    identifier: bpy.props.StringProperty()


    def draw_node(self,context,layout):
        layout.prop_search(self, "search_value", self.node_tree, "sn_variables", text="")

        if self.search_value != "" and not self.search_value in self.node_tree.sn_variables:
            self.outputs.clear()


    def code_evaluate(self, context, touched_socket):
        return {
            "code": self.get_python_name(self.node_tree.name) + '["' + self.node_tree.sn_variables[self.search_value].identifier + '"]'
        }