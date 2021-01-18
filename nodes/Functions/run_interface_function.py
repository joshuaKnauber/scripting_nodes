import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_RunLayoutFunctionNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RunLayoutFunctionNode"
    bl_label = "Run Interface Function"
    # bl_icon = "GRAPH"
    bl_width_default = 200

    node_options = {
        "default_color": (0.2,0.2,0.2),
    }

    recursion_warning: bpy.props.BoolProperty()
    func_uid: bpy.props.StringProperty()

    def on_outside_update(self,node):
        if node == self:
            for graph in self.addon_tree.sn_graphs:
                for graph_node in graph.node_tree.nodes:
                    if graph_node.uid == self.func_uid:
                        node = graph_node

        else:
            if node.bl_idname == "SN_InterfaceFunctionNode":
                if self.func_uid == node.uid:
                    self["func_name"] = node.func_name
                if not self.func_name in self.addon_tree.sn_nodes["SN_InterfaceFunctionNode"].items and self.func_name != "":
                    self.func_name = ""


        if node.bl_idname == "SN_InterfaceFunctionNode":
            if node.uid == self.func_uid:
                parameters = []
                for out in node.outputs:
                    if not out.bl_idname in ["SN_DynamicVariableSocket", "SN_InterfaceSocket", "SN_DynamicInterfaceSocket"]:
                        parameters.append([out.variable_name, out.bl_idname, out.subtype])

                if len(parameters) != len(self.inputs[1:]):
                    if len(parameters) > len(self.inputs[1:]):
                        input_len = len(self.inputs)-1
                        for x, parameter in enumerate(parameters):
                            if x >= input_len:
                                inp = self.add_input(parameter[1],parameter[0])

                    else:
                        removed = False
                        for x, parameter in enumerate(parameters):
                            if parameter[0] != self.inputs[x+1].default_text:
                                removed = True
                                self.inputs.remove(self.inputs[x+1])
                        if not removed:
                            self.inputs.remove(self.inputs[-1])


                for x, parameter in enumerate(parameters):
                    self.inputs[x+1].default_text = parameter[0]
                    self.inputs[x+1].subtype = parameter[2]


    def update_name(self, context):
        self.recursion_warning = False
        if self.func_name in self.addon_tree.sn_nodes["SN_InterfaceFunctionNode"].items:
            item = self.addon_tree.sn_nodes["SN_InterfaceFunctionNode"].items[self.func_name]
            if item.node_uid != self.func_uid:
                for i, inp in enumerate(self.inputs):
                    if i:
                        try: self.inputs.remove(inp)
                        except: pass
                self.func_uid = item.node_uid

            if self.what_start_idname() == "SN_InterfaceFunctionNode":
                if self.func_name == self.what_start_node().func_name:
                    self.recursion_warning = True

            self.on_outside_update(self)
        else:
            self.func_uid = ""
            for i, inp in enumerate(self.inputs):
                if i:
                    try: self.inputs.remove(inp)
                    except: pass

        self.auto_compile(context)


    func_name: bpy.props.StringProperty(name="Name", description="Name of the function", update=update_name)

    def on_node_update(self):
        self.recursion_warning = False
        if self.what_start_idname() == "SN_InterfaceFunctionNode":
            if self.func_name == self.what_start_node().func_name:
                self.recursion_warning = True

    def on_create(self,context):
        self.add_required_to_collection(["SN_InterfaceFunctionNode"])
        self.add_interface_input("Run Layout Function")

    def draw_node(self,context,layout):
        if self.recursion_warning:
            layout.label(text="Be careful when using recursion!")

        layout.prop_search(self, "func_name", self.addon_tree.sn_nodes["SN_InterfaceFunctionNode"], "items")


    def code_evaluate(self, context, touched_socket):
        if self.func_name in self.addon_tree.sn_nodes["SN_InterfaceFunctionNode"].items:
            parameters = []
            for inp in self.inputs[1:]:
                parameters.append(inp.code() + ", ")
            layout = touched_socket.links[0].from_node.what_layout(touched_socket.links[0].from_socket)

            return {
                "code": f"""
                        {self.addon_tree.sn_nodes["SN_InterfaceFunctionNode"].items[self.func_name].identifier}({layout}, {self.list_code(parameters)})
                        """
            }

        else:
            self.add_error("No function", "No valid function selected")
            return {
                "code": f"""
                        """
            }