import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup
from ...compiler.compiler import get_module



class SN_OT_RunFunction(bpy.types.Operator):
    bl_idname = "sn.test_function"
    bl_label = "Test Run"
    bl_description = "Runs this node"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    node: bpy.props.StringProperty()

    def execute(self, context):
        node = context.space_data.node_tree.nodes[self.node]
        module = get_module(node.addon_tree)
        if module:
            try:
                func_call = node.code_evaluate(context, node.inputs[0])["code"].split("\n")
                func_call = func_call[1]

                # Function
                if "=" in func_call.split("(")[0]:
                    func_call = func_call.split("=")[-1]
                    func_call = func_call.strip()
                    exec("module." + func_call)

                # Operator
                else:
                    func_call = func_call.strip()
                    exec("module.exec_line(\"\"\"" + func_call + "\"\"\")")
            
            except:
                self.report({"ERROR"},message="Failed to run! This button might not work for all cases.")
        return {"FINISHED"}



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
            if self.use_execute:
                self.remove_output_range(1)
            else:
                self.outputs.clear()

        if self.search_value in self.return_collection:
            if self.use_execute:
                index = 1
            else:
                index = 0
            for graph in self.addon_tree.sn_graphs:
                for node in graph.node_tree.nodes:
                    if node.bl_idname == "SN_ReturnNode":
                        if node.uid == self.return_collection[self.search_value].node_uid:
                            length = len(self.outputs) if self.use_execute else len(self.outputs)+1
                            if length != len(node.inputs)-1:
                                if self.use_execute:
                                    self.remove_output_range(1)
                                else:
                                    self.outputs.clear()
                                self.make_collection("NAME_CHANGE")

                            parameters = []
                            for inp in node.inputs[1:]:
                                if inp.bl_idname != "SN_DynamicVariableSocket":
                                    parameters.append([inp.variable_name, inp.bl_idname])
                            for x, parameter in enumerate(parameters):
                                self.outputs[x+index].default_text = parameter[0]


    def make_collection(self, parameter=""):
        self.return_collection.clear()
        for graph in self.addon_tree.sn_graphs:
            for node in graph.node_tree.nodes:
                if node.bl_idname == "SN_ReturnNode" and not node.connected_function in ["None", ""] and node.connected_function in self.addon_tree.sn_nodes["SN_FunctionNode"].items:
                    if self.addon_tree.sn_nodes["SN_FunctionNode"].items[node.connected_function].node_uid == self.func_uid:
                        item = self.return_collection.add()
                        item.name = node.name
                        item.node_uid = node.uid

                    elif node.connected_function == self.func_name:
                        item = self.return_collection.add()
                        item.name = node.name
                        item.node_uid = node.uid


        if self.search_value in self.return_collection:
            if self.use_execute:
                index = 1
            else:
                index = 0
            for graph in self.addon_tree.sn_graphs:
                for node in graph.node_tree.nodes:
                    if node.bl_idname == "SN_ReturnNode":
                        if node.uid == self.return_collection[self.search_value].node_uid:
                            parameters = []
                            for inp in node.inputs[1:]:
                                if inp.bl_idname != "SN_DynamicVariableSocket":
                                    if inp.bl_idname == "SN_BlendDataSocket":
                                        parameters.append([inp.variable_name, inp.bl_idname, inp.subtype, inp.data_type, inp.data_name, inp.data_identifier, inp.data_type_collection])
                                    else:
                                        parameters.append([inp.variable_name, inp.bl_idname, inp.subtype])

                            if len(parameters) != len(self.outputs[index:]):
                                if len(parameters) > len(self.outputs[index:]):
                                    output_len = len(self.outputs)-index
                                    for x, parameter in enumerate(parameters):
                                        if x >= output_len:
                                            out = self.add_output(parameter[1],parameter[0])

                                else:
                                    removed = False
                                    for x, parameter in enumerate(parameters):
                                        if parameter[0] != self.outputs[x+index].default_text:
                                            removed = True
                                            self.outputs.remove(self.outputs[x+index])
                                    if not removed:
                                        self.outputs.remove(self.outputs[-1])

                            for x, parameter in enumerate(parameters):
                                self.outputs[x+index].default_text = parameter[0]
                                self.outputs[x+index].subtype = parameter[2]
                                if self.outputs[x+index].bl_idname == "SN_BlendDataSocket":
                                    self.outputs[x+index].data_type = parameter[3]
                                    self.outputs[x+index].data_type_collection = parameter[6]
                                    self.outputs[x+index].data_name = parameter[4]
                                    self.outputs[x+index].data_identifier = parameter[5]


        else:
            if self.use_execute:
                self.remove_output_range(1)
            else:
                self.outputs.clear()
        if parameter != "NAME_CHANGE":
            self.update_return(None)

    def update_execute(self, context):
        if self.use_execute:
            inp = self.add_execute_input("Run Function")
            self.inputs.move(len(self.inputs)-1, 0)
            out = self.add_execute_output("Execute").mirror_name = True
            self.outputs.move(len(self.outputs)-1, 0)
        else:
            self.inputs.remove(self.inputs[0])
            self.outputs.remove(self.outputs[0])


    recursion_warning: bpy.props.BoolProperty()
    func_uid: bpy.props.StringProperty()
    search_value: bpy.props.StringProperty(name="Search value", update=update_return)
    return_collection: bpy.props.CollectionProperty(type=SN_GenericPropertyGroup)
    use_execute: bpy.props.BoolProperty(default=True, name="Use Execute", description="Function will run on every output access if disabled", update=update_execute)


    def on_outside_update(self,node):
        if node == self:
            for graph in self.addon_tree.sn_graphs:
                for graph_node in graph.node_tree.nodes:
                    if not graph_node.bl_idname in ["NodeFrame","NodeReroute"]:
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
                        if out.bl_idname == "SN_StringSocket":
                            parameters.append([out.variable_name, out.bl_idname, out.subtype, out.enum_values])
                        else:
                            parameters.append([out.variable_name, out.bl_idname, out.subtype])
                
                if self.use_execute:
                    index = 1
                else:
                    index = 0

                if len(parameters) != len(self.inputs[index:]):
                    if len(parameters) > len(self.inputs[index:]):
                        input_len = len(self.inputs)-index
                        for x, parameter in enumerate(parameters):
                            if x >= input_len:
                                inp = self.add_input(parameter[1],parameter[0])

                    else:
                        removed = False
                        for x, parameter in enumerate(parameters):
                            if parameter[0] != self.inputs[x+index].default_text:
                                removed = True
                                self.inputs.remove(self.inputs[x+index])
                        if not removed:
                            self.inputs.remove(self.inputs[-1])


                for x, parameter in enumerate(parameters):
                    self.inputs[x+index].default_text = parameter[0]
                    self.inputs[x+index].subtype = parameter[2]
                    if self.inputs[x+index].bl_idname == "SN_StringSocket":
                        self.inputs[x+index].enum_values = parameter[3]

        else:
            self.make_collection()


    def update_name(self, context):
        self.recursion_warning = False
        if self.func_name in self.addon_tree.sn_nodes["SN_FunctionNode"].items:
            item = self.addon_tree.sn_nodes["SN_FunctionNode"].items[self.func_name]
            if item.node_uid != self.func_uid:
                if self.use_execute:
                    self.remove_input_range(1)
                else:
                    self.inputs.clear()
                self.func_uid = item.node_uid

            if self.what_start_idname() == "SN_FunctionNode":
                if self.func_name == self.what_start_node().func_name:
                    self.recursion_warning = True

            self.on_outside_update(self)
            self.make_collection()
        else:
            self.func_uid = ""
            self.search_value = ""
            if self.use_execute:
                self.remove_input_range(1)
            else:
                self.inputs.clear()
            self.make_collection()

        self.auto_compile()


    func_name: bpy.props.StringProperty(name="Name", description="Name of the function", update=update_name)

    def on_node_update(self):
        self.recursion_warning = False
        if self.what_start_idname() == "SN_FunctionNode":
            if self.func_name == self.what_start_node().func_name:
                self.recursion_warning = True

    def on_create(self,context):
        self.add_required_to_collection(["SN_FunctionNode"])
        self.add_execute_input("Run Function")
        self.add_execute_output("Execute").mirror_name = True

    def draw_node(self,context,layout):
        layout.prop(self, "use_execute")

        row = layout.row()
        row.scale_y = 1.2
        row.enabled = get_module(self.addon_tree) != None and self.func_name != ""
        op = row.operator("sn.test_function",text="Run Function",icon="PLAY")
        op.node = self.name

        if self.recursion_warning:
            layout.label(text="Be careful when using recursion!")

        layout.prop_search(self, "func_name", self.addon_tree.sn_nodes["SN_FunctionNode"], "items")
        if len(self.return_collection):
            layout.prop_search(self, "search_value", self, "return_collection", text="")


    def code_evaluate(self, context, touched_socket):
        if self.func_name in self.addon_tree.sn_nodes["SN_FunctionNode"].items:
            index = 1 if self.use_execute else 0
            parameters = []
            for inp in self.inputs[index:]:
                parameters.append(inp.code() + ", ")


            if not self.use_execute:
                return {"code": f"""{self.addon_tree.sn_nodes["SN_FunctionNode"].items[self.func_name].identifier}({self.list_code(parameters)})[{self.outputs.find(touched_socket.name)}]"""}

            if touched_socket == self.inputs[0]:
                return {
                    "code": f"""
                            function_return_{self.uid} = {self.addon_tree.sn_nodes["SN_FunctionNode"].items[self.func_name].identifier}({self.list_code(parameters)})
                            {self.outputs[0].code(7)}
                            """
                }

            elif self.inputs[0].is_linked:
                return {
                    "code": f"""function_return_{self.uid}[{self.outputs.find(touched_socket.name)-1}]"""
                }
            else:
                self.add_error("No run function", "You need to run your function first")
                return {"code": "None"}

        else:
            self.add_error("No function", "No valid function selected")
            return {
                "code": f"""
                        {self.outputs[0].code(6)}
                        """
            }