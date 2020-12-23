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

    recursion_warning: bpy.props.BoolProperty()
    func_uid: bpy.props.StringProperty()

    def on_outside_update(self,node,parameter=""):
        if node == self:
            for graph in self.addon_tree.sn_graphs:
                for graph_node in graph.node_tree.nodes:
                    if graph_node.uid == self.func_uid:
                        node = graph_node

        else:
            if node.bl_idname == "SN_ReturnNode" and parameter == "ON_FREE":
                for index, out in enumerate(self.outputs):
                    if index > 0:
                        self.outputs.remove(out)
                return
            else:
                if self.func_uid == node.uid:
                    self.func_name = node.func_name
                if not self.func_name in self.addon_tree.sn_nodes["SN_FunctionNode"].items and self.func_name != "":
                    self.func_name = ""


        if node.bl_idname == "SN_ReturnNode" and parameter != "ON_FREE":
            start_node = node.what_start_node()
            if start_node.bl_idname == "SN_FunctionNode":
                if start_node.uid == self.func_uid:
                    return_types = []
                    for inp in node.inputs[1:]:
                        if inp.bl_idname != "SN_DynamicVariableSocket":
                            return_types.append([inp.var_name, inp.bl_idname])

                    if len(return_types) > len(self.outputs[1:]):
                        output_len = len(self.outputs)-1
                        for x, return_type in enumerate(return_types):
                            if x >= output_len:
                                out = self.add_output(return_type[1],return_type[0],False)

                    elif len(return_types) < len(self.outputs[1:]):
                        removed = False
                        for x, return_type in enumerate(return_types):
                            if return_type[0] != self.outputs[x+1].name:
                                removed = True
                                self.outputs.remove(self.outputs[x+1])
                        if not removed:
                            self.outputs.remove(self.outputs[-1])


                    for x, return_type in enumerate(return_types):
                        self.outputs[x+1].name = return_type[0]


        else:
            if node.uid == self.func_uid:
                parameters = []
                for out in node.outputs[1:]:
                    if out.bl_idname != "SN_DynamicVariableSocket":
                        parameters.append([out.var_name, out.bl_idname])

                if len(parameters) != len(self.inputs[1:]):
                    if len(parameters) > len(self.inputs[1:]):
                        input_len = len(self.inputs)-1
                        for x, parameter in enumerate(parameters):
                            if x >= input_len:
                                self.add_input(parameter[1],parameter[0],False)

                    else:
                        removed = False
                        for x, parameter in enumerate(parameters):
                            if parameter[0] != self.inputs[x+1].name:
                                removed = True
                                self.inputs.remove(self.inputs[x+1])
                        if not removed:
                            self.inputs.remove(self.inputs[-1])


                for x, parameter in enumerate(parameters):
                    self.inputs[x+1].name = parameter[0]


    def update_name(self, context):
        self.recursion_warning = False
        if self.func_name in self.addon_tree.sn_nodes["SN_FunctionNode"].items:
            item = self.addon_tree.sn_nodes["SN_FunctionNode"].items[self.func_name]
            if item.node_uid != self.func_uid:
                for inp in self.inputs[1:]:
                    try: self.inputs.remove(inp)
                    except: pass
                for out in self.outputs[1:]:
                    try: self.outputs.remove(out)
                    except: pass
                self.func_uid = item.node_uid

            if self.what_start_idname() == "SN_FunctionNode":
                if self.func_name == self.what_start_node().func_name:
                    self.recursion_warning = True
            self.on_outside_update(self)
            self.update_nodes_by_type("SN_ReturnNode")
        else:
            self.func_uid = ""
            for inp in self.inputs[1:]:
                try: self.inputs.remove(inp)
                except: pass
            for out in self.outputs[1:]:
                try: self.outputs.remove(out)
                except: pass

        self.update_needs_compile(context)


    func_name: bpy.props.StringProperty(name="Name", description="Name of the function", update=update_name)

    def on_node_update(self):
        self.recursion_warning = False
        if self.what_start_idname() == "SN_FunctionNode":
            if self.func_name == self.what_start_node().func_name:
                self.recursion_warning = True

    def on_create(self,context):
        self.add_execute_input("Execute")
        self.add_execute_output("Execute")


    def draw_node(self,context,layout):
        if self.recursion_warning:
            layout.label(text="Be careful when using recursion!")

        layout.prop_search(self, "func_name", self.addon_tree.sn_nodes["SN_FunctionNode"], "items")


    def code_evaluate(self, context, touched_socket):
        if self.func_name in self.addon_tree.sn_nodes["SN_FunctionNode"].items:
            parameters = []
            for inp in self.inputs[1:]:
                parameters.append(inp.value + ", ")

            if touched_socket == self.inputs[0]:
                return {
                    "code": f"""
                            {self.addon_tree.sn_nodes["SN_FunctionNode"].items[self.func_name].identifier}({self.list_blocks(parameters, 0)})
                            {self.outputs[0].block(7)}
                            """
                }

            else:
                return {
                    "code": f"""{self.addon_tree.sn_nodes["SN_FunctionNode"].items[self.func_name].identifier}({self.list_blocks(parameters, 0)})[{self.outputs.find(touched_socket.name)-1}]"""
                }

        else:
            self.add_error("No function", "No valid function selected")
            return {
                "code": f"""
                        {self.outputs[0].block(6)}
                        """
            }