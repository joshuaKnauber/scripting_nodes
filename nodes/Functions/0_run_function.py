import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_RunFunctionNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RunFunctionNode"
    bl_label = "Run Function"
    # bl_icon = "GRAPH"
    bl_width_default = 200

    node_options = {
        "default_color": (0.2,0.2,0.2),
    }

    def update_return(self, context):
        if not self.search_value:
            for i, out in enumerate(self.outputs):
                if i:
                    try: self.outputs.remove(out)
                    except: pass

        if self.search_value in self.return_collection:
            for graph in self.addon_tree.sn_graphs:
                for node in graph.node_tree.nodes:
                    if node.bl_idname == "SN_ReturnNode":
                        if node.uid == self.return_collection[self.search_value].node_uid:
                            if len(self.outputs) != len(node.inputs)-1:
                                for i, out in enumerate(self.outputs):
                                    if i:
                                        try: self.outputs.remove(out)
                                        except: pass
                                self.make_collection("NAME_CHANGE")

                            parameters = []
                            for inp in node.inputs[1:]:
                                if inp.bl_idname != "SN_DynamicVariableSocket":
                                    parameters.append([inp.variable_name, inp.bl_idname])
                            for x, parameter in enumerate(parameters):
                                self.outputs[x+1].default_text = parameter[0]


    def make_collection(self, parameter=""):
        self.return_collection.clear()
        for graph in self.addon_tree.sn_graphs:
            for node in graph.node_tree.nodes:
                if node.bl_idname == "SN_ReturnNode" and not node.connected_function in ["None", ""]:
                    if self.addon_tree.sn_nodes["SN_FunctionNode"].items[node.connected_function].node_uid == self.func_uid:
                        item = self.return_collection.add()
                        item.name = node.name
                        item.node_uid = node.uid

                    elif node.connected_function == self.func_name:
                        item = self.return_collection.add()
                        item.name = node.name
                        item.node_uid = node.uid


        if self.search_value in self.return_collection:
            for graph in self.addon_tree.sn_graphs:
                for node in graph.node_tree.nodes:
                    if node.bl_idname == "SN_ReturnNode":
                        if node.uid == self.return_collection[self.search_value].node_uid:
                            parameters = []
                            for inp in node.inputs[1:]:
                                if inp.bl_idname != "SN_DynamicVariableSocket":
                                    parameters.append([inp.variable_name, inp.bl_idname])

                            if len(parameters) != len(self.outputs[1:]):
                                if len(parameters) > len(self.outputs[1:]):
                                    output_len = len(self.outputs)-1
                                    for x, parameter in enumerate(parameters):
                                        if x >= output_len:
                                            out = self.add_output(parameter[1],parameter[0])

                                else:
                                    removed = False
                                    for x, parameter in enumerate(parameters):
                                        if parameter[0] != self.outputs[x+1].default_text:
                                            removed = True
                                            self.outputs.remove(self.outputs[x+1])
                                    if not removed:
                                        self.outputs.remove(self.outputs[-1])

                            for x, parameter in enumerate(parameters):
                                self.outputs[x+1].default_text = parameter[0]


        else:
            for i, out in enumerate(self.outputs):
                if i:
                    try: self.outputs.remove(out)
                    except: pass
        if parameter != "NAME_CHANGE":
            self.update_return(None)


    recursion_warning: bpy.props.BoolProperty()
    func_uid: bpy.props.StringProperty()
    search_value: bpy.props.StringProperty(name="Search value", update=update_return)
    return_collection: bpy.props.CollectionProperty(type=SN_GenericPropertyGroup)

    def on_outside_update(self,node):
        if node == self:
            for graph in self.addon_tree.sn_graphs:
                for graph_node in graph.node_tree.nodes:
                    if graph_node.uid == self.func_uid:
                        node = graph_node

        else:
            if node.bl_idname == "SN_FunctionNode":
                if self.func_uid == node.uid:
                    self["func_name"] = node.func_name
                if not self.func_name in self.addon_tree.sn_nodes["SN_FunctionNode"].items and self.func_name != "":
                    self.func_name = ""


        if node.bl_idname == "SN_FunctionNode":
            if node.uid == self.func_uid:
                parameters = []
                for out in node.outputs[1:]:
                    if out.bl_idname != "SN_DynamicVariableSocket":
                        parameters.append([out.variable_name, out.bl_idname])

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

        else:
            self.make_collection()


    def update_name(self, context):
        self.recursion_warning = False
        if self.func_name in self.addon_tree.sn_nodes["SN_FunctionNode"].items:
            item = self.addon_tree.sn_nodes["SN_FunctionNode"].items[self.func_name]
            if item.node_uid != self.func_uid:
                for i, inp in enumerate(self.inputs):
                    if i:
                        try: self.inputs.remove(inp)
                        except: pass
                self.func_uid = item.node_uid

            if self.what_start_idname() == "SN_FunctionNode":
                if self.func_name == self.what_start_node().func_name:
                    self.recursion_warning = True

            self.on_outside_update(self)
            self.make_collection()
        else:
            self.func_uid = ""
            self.search_value = ""
            for i, inp in enumerate(self.inputs):
                if i:
                    try: self.inputs.remove(inp)
                    except: pass
            self.make_collection()

        self.auto_compile(context)


    func_name: bpy.props.StringProperty(name="Name", description="Name of the function", update=update_name)

    def on_node_update(self):
        self.recursion_warning = False
        if self.what_start_idname() == "SN_FunctionNode":
            if self.func_name == self.what_start_node().func_name:
                self.recursion_warning = True

    def on_create(self,context):
        self.add_execute_input("Run Function")
        self.add_execute_output("Execute")

    def draw_node(self,context,layout):
        if self.recursion_warning:
            layout.label(text="Be careful when using recursion!")

        layout.prop_search(self, "func_name", self.addon_tree.sn_nodes["SN_FunctionNode"], "items")
        if len(self.return_collection):
            layout.prop_search(self, "search_value", self, "return_collection", text="")


    def code_evaluate(self, context, touched_socket):
        if self.func_name in self.addon_tree.sn_nodes["SN_FunctionNode"].items:
            parameters = []
            for inp in self.inputs[1:]:
                parameters.append(inp.code() + ", ")

            if touched_socket == self.inputs[0]:
                return {
                    "code": f"""
                            {self.addon_tree.sn_nodes["SN_FunctionNode"].items[self.func_name].identifier}({self.list_code(parameters)})
                            {self.outputs[0].code(7)}
                            """
                }

            else:
                return {
                    "code": f"""{self.addon_tree.sn_nodes["SN_FunctionNode"].items[self.func_name].identifier}({self.list_code(parameters)})[{self.outputs.find(touched_socket.name)-1}]"""
                }

        else:
            self.add_error("No function", "No valid function selected")
            return {
                "code": f"""
                        {self.outputs[0].code(6)}
                        """
            }