import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_InterfaceFunctionNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_InterfaceFunctionNode"
    bl_label = "Interface Function"
    # bl_icon = "GRAPH"
    bl_width_default = 200

    node_options = {
        "default_color": (0.2,0.2,0.2),
        "starts_tree": True,
        "collection_name_attr": "func_name",
        "has_collection": True
    }

    def update_name(self, context):
        if not self.func_name:
            self["func_name"] = "New Interface Function"

        self.update_item_name()
        self.item.identifier = self.get_python_name(self.func_name, "new_interface_function")
        self["func_name"] = self.get_unique_name(self.func_name, self.collection.items, " ")

        self.item.identifier = self.get_python_name(self.func_name, "new_interface_function")
        self.auto_compile()

        self.update_nodes_by_type("SN_RunLayoutFunctionNode")

    func_name: bpy.props.StringProperty(name="Name", description="Name of the function", update=update_name)

    def on_create(self,context):
        self.add_interface_output("Layout")
        self.add_dynamic_interface_output("Layout")
        out = self.add_dynamic_variable_output("Parameter")
        out.show_var_name = True
        out.edit_var_name = True
        out.return_var_name = True
        self.update_name(None)


    def on_dynamic_add(self,socket, connected_socket):
        if socket.bl_idname != "SN_InterfaceSocket":
            if connected_socket:
                socket.subtype = connected_socket.subtype
            if connected_socket and connected_socket.name != "":
                socket.variable_name = connected_socket.name
            else:
                socket.variable_name = "Parameter"

    def on_dynamic_remove(self,is_output):
        self.update_nodes_by_type("SN_RunLayoutFunctionNode")

    def on_var_name_update(self,socket):
        if socket.variable_name == "Layout":
            socket.variable_name = "Layout 001"
        names = []
        for out in self.outputs:
            if out.bl_idname != "SN_InterfaceSocket":
                names.append(out.variable_name)

        socket["variable_name"] = self.get_unique_name(socket.variable_name, names, separator=" ")
        self.update_nodes_by_type("SN_RunLayoutFunctionNode")


    def draw_node(self,context,layout):
        layout.prop(self, "func_name")

    def on_free(self):
        self.update_nodes_by_type("SN_RunLayoutFunctionNode")

    def code_evaluate(self, context, touched_socket):
        if touched_socket:
            return {
                "code": f"""{touched_socket.code()}"""
            }


    def code_imperative(self, context):
        parameter_string = ""
        for out in self.outputs:
            if not out.bl_idname in ["SN_DynamicVariableSocket", "SN_InterfaceSocket", "SN_DynamicInterfaceSocket"]:
                parameter_string+=out.code()+", "

        return {
            "code": f"""
                    def {self.item.identifier}(layout, {parameter_string}):
                        try:
                            {self.outputs["Layout"].by_name(7) if self.outputs["Layout"].by_name().strip() else "pass"}
                        except Exception as exc:
                            print(str(exc) + " | Error in function {self.func_name}")
                    """
        }