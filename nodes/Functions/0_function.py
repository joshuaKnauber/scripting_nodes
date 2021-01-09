import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_FunctionNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_FunctionNode"
    bl_label = "Function"
    # bl_icon = "GRAPH"
    bl_width_default = 200

    node_options = {
        "default_color": (0.2,0.2,0.2),
        "starts_tree": True,
        "has_collection": True
    }

    def update_name(self, context):
        if not self.func_name:
            self.func_name = "New Function"

        self.item.name = self.func_name
        self.item.identifier = self.get_python_name(self.func_name, "new_function")

        unique_name = self.get_unique_name(self.func_name, self.collection.items, " ")
        if unique_name != self.func_name:
            self.func_name = unique_name

        self.item.name = self.func_name
        self.item.identifier = self.get_python_name(self.func_name, "new_function")
        self.update_nodes_by_type("SN_ReturnNode")
        self.auto_compile(context)


    func_name: bpy.props.StringProperty(name="Name", description="Name of the function", update=update_name)


    def on_create(self,context):
        self.add_execute_output("Function")
        out = self.add_dynamic_variable_output("Parameter")
        out.show_var_name = True
        out.edit_var_name = True
        out.return_var_name = True
        self.update_name(None)


    def on_dynamic_add(self,socket, connected_socket):
        if connected_socket and connected_socket.name != "":
            socket.variable_name = connected_socket.name
        else:
            socket.variable_name = "Parameter"

    def on_var_name_update(self,socket):
        names = []
        for out in self.outputs[1:-1]:
            names.append(out.variable_name)

        socket["variable_name"] = self.get_unique_name(socket.variable_name, names, separator=" ")
        self.update_nodes_by_type("SN_RunFunctionNode")


    def on_any_change(self):
        self.update_nodes_by_type("SN_RunFunctionNode")


    def draw_node(self,context,layout):
        layout.prop(self, "func_name")


    def on_free(self):
        self.update_nodes_by_type("SN_RunFunctionNode")


    def code_evaluate(self, context, touched_socket):
        if touched_socket:
            return {
                "code": f"""{touched_socket.code()}"""
            }


    def code_imperative(self, context):
        parameter_string = ""
        for out in self.outputs[1:-1]:
            parameter_string+=out.code()+", "


        return {
            "code": f"""
                    def {self.item.identifier}({parameter_string}):
                        try:
                            {self.outputs[0].code(7) if self.outputs[0].code() else "pass"}
                        except Exception as exc:
                            print(str(exc) + " | Error in function {self.func_name}")
                    """
        }