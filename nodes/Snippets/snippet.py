import bpy
import json
import os
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_OT_SaveSnippet(bpy.types.Operator):
    bl_idname = "sn.save_snippet"
    bl_label = "Save Snippet"
    bl_description = "Saves this run function node as a snippet"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    filepath: bpy.props.StringProperty(name="File Path", description="Filepath used for exporting the file", maxlen=1024, subtype='FILE_PATH')

    filename_ext = ".json"
    filter_glob: bpy.props.StringProperty(default='*.json', options={'HIDDEN'})

    def function_node(self, context):
        node = context.space_data.node_tree.nodes.active
        if node.bl_idname == "SN_RunFunctionNode":
            return node.addon_tree.sn_nodes["SN_FunctionNode"].items[node.func_name].node()
        else:
            return node.addon_tree.sn_nodes["SN_InterfaceFunctionNode"].items[node.func_name].node()

    def get_all_connected(self, node, visited):
        nodes = [node]
        visited.append(node)
        for out in node.outputs:
            for link in out.links:
                if not link.to_node in visited:
                    nodes += self.get_all_connected(link.to_node, visited)
        for inp in node.inputs:
            for link in inp.links:
                if not link.from_node in visited:
                    nodes += self.get_all_connected(link.from_node, visited)
        return nodes

    def get_used_variables(self, start_node):
        vars = []
        var_names = {}
        for node in (self.get_used_functions(start_node) + [start_node]):
            for node in list(set(self.get_all_connected(node, []))):
                if node.bl_idname in ["SN_GetVariableNode", "SN_SetVariableNode", "SN_ChangeVariableNode", "SN_ResetVariableNode", "SN_AddToListNode", "SN_RemoveFromListNode"]:
                    if node.search_value in node.node_tree.sn_variables and not node.search_value in vars:
                        vars.append(node.search_value)
                        var_names[node.node_tree.sn_variables[node.search_value].identifier] = [node.search_value, node.node_tree.sn_variables[node.search_value].var_type]
        return vars, var_names

    def get_used_properties(self, start_node):
        props = []
        for node in (self.get_used_functions(start_node) + [start_node]):
            for node in list(set(self.get_all_connected(node, []))):
                if node.bl_idname in ["SN_GetPropertyNode", "SN_SetPropertyNode"]:
                    if node.prop_name in node.node_tree.sn_properties:
                        props.append(node.node_tree.sn_properties[node.prop_name])
        return props

    def get_used_functions(self, start_node):
        function_nodes = []
        for node in list(set(self.get_all_connected(start_node, []))):
            if node.bl_idname == "SN_RunFunctionNode" and "SN_FunctionNode" in node.addon_tree.sn_nodes and node.func_name in node.addon_tree.sn_nodes["SN_FunctionNode"].items:
                function_node = node.addon_tree.sn_nodes["SN_FunctionNode"].items[node.func_name].node()
                function_nodes.append(function_node)
                function_nodes += self.get_used_functions(function_node)
            elif node.bl_idname == "SN_InterfaceFunctionNode" and "SN_InterfaceFunctionNode" in node.addon_tree.sn_nodes and node.func_name in node.addon_tree.sn_nodes["SN_InterfaceFunctionNode"].items:
                function_node = node.addon_tree.sn_nodes["SN_InterfaceFunctionNode"].items[node.func_name].node()
                function_nodes.append(function_node)
                function_nodes += self.get_used_functions(function_node)
        return function_nodes


    def get_variable_code(self, node):
        used_variables = list(set(self.get_used_variables(node)[0]))
        code = ""
        for var in used_variables:
            code += node.node_tree.sn_variables[var].variable_register()
        return "SNIPPET_VARS = {" + code + "}"

    def get_prop_register(self, props):
        code = "\n"
        for prop in props:
            code += f"if not '{prop.identifier}' in bpy.types.{prop.attach_property_to}.bl_rna.properties: {prop.property_register()}"
        return code

    def get_prop_unregister(self, props):
        code = "\n"
        for prop in props:
            code += f"if '{prop.identifier}' in bpy.types.{prop.attach_property_to}.bl_rna.properties: {prop.property_unregister()}"
        return code

    def get_function_def(self, function_nodes, context):
        code = {}
        for node in function_nodes:
            node_code = node.code_imperative(context)["code"]
            og_name = node.get_python_name(node.node_tree.name) + "["
            node_code = node_code.replace(og_name, "SNIPPET_VARS[")
            code[node.uid] = node_code
        return code

    def get_socket_attributes(self, socket):
        attributes = {}
        for attr in socket.copy_attributes:
            value = getattr(socket, attr)
            if "array" in str(type(value)).lower() or "color" in str(type(value)).lower():
                temp_value = value
                value = []
                for i in temp_value:
                    value.append(i)
                value = tuple(value)
            attributes[attr] = value
        return attributes

    def get_snippet(self, context):
        run_node = context.space_data.node_tree.nodes.active
        node = self.function_node(context)
        data = { "name":node.func_name, "uid": run_node.uid,
                "function":"", "register":"", "unregister":"", "properties":[],
                "func_name":node.item.identifier,
                "inputs":[], "outputs":[] }

        for inp in run_node.inputs:
            data["inputs"].append({"idname":inp.bl_idname, "name":inp.get_text(), "subtype":inp.subtype, "attributes":self.get_socket_attributes(inp)})

        for out in run_node.outputs:
            data["outputs"].append({"idname":out.bl_idname, "name":out.get_text(), "subtype":out.subtype, "attributes":self.get_socket_attributes(inp)})

        # get function code
        code = node.code_imperative(context)["code"]

        # get variable definitions
        code = " "*len(code.replace("\n","").split("def")[0]) + self.get_variable_code(node) + code
        
        # replace variable calls
        og_name = node.get_python_name(node.node_tree.name) + "["
        code = code.replace(og_name, "SNIPPET_VARS[")

        data["function"] = code

        data["variable_definitions"] = self.get_used_variables(node)[1]
        data["function_definitions"] = self.get_function_def(self.get_used_functions(node), context)
        props = list(set(self.get_used_properties(node)))
        data["register"] = self.get_prop_register(props)
        data["unregister"] = self.get_prop_unregister(props)
        data["property_identifiers"] = {}
        for prop in props:
            data["property_identifiers"][prop.identifier] = [prop.name, prop.var_type, prop.attach_property_to]

        return json.dumps(data, indent=4)

    def execute(self, context):
        with open(self.filepath, "w") as json_file:
            json_file.write(self.get_snippet(context))
        self.report({"INFO"},message="Snippet saved")
        return {"FINISHED"}

    def invoke(self, context, event):
        name = self.function_node(context).func_name + ".json"
        self.filepath = os.path.join(self.filepath, name)

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class SN_VarPropertyGroup(bpy.types.PropertyGroup):

    def update_name(self, context):
        if self.is_prop:
            if self.name in self.node().node_tree.sn_properties:
                if self.node().node_tree.sn_properties[self.name].var_type != self.type or self.node().node_tree.sn_properties[self.name].attach_property_to != self.attach_property_to:
                    self["name"] = ""
                    self.new_identifier = ""
                else:
                    self.new_identifier = self.node().node_tree.sn_properties[self.name].identifier
            else:
                self["name"] = ""
                self.new_identifier = ""

        else:
            if self.name in self.node().node_tree.sn_variables:
                if self.node().node_tree.sn_variables[self.name].var_type != self.type:
                    self["name"] = ""
                    self.new_identifier = ""
                else:
                    self.new_identifier = self.node().node_tree.sn_variables[self.name].identifier
            else:
                self["name"] = ""
                self.new_identifier = ""
        self.node().auto_compile()

    name: bpy.props.StringProperty(name="Name of the Variable", update=update_name)
    new_identifier: bpy.props.StringProperty()
    og_name: bpy.props.StringProperty()
    is_prop: bpy.props.BoolProperty(default=False)
    type: bpy.props.StringProperty()
    identifier: bpy.props.StringProperty()
    attach_property_to: bpy.props.StringProperty()
    node_uid: bpy.props.StringProperty()

    def node(self):
        for graph in bpy.context.scene.sn.addon_tree().sn_graphs:
            for node in graph.node_tree.nodes:
                if not node.bl_idname in ["NodeFrame","NodeReroute"]:
                    if node.uid == self.node_uid:
                        return node


class SN_SnippetNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SnippetNode"
    bl_label = "Snippet"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3)
    }

    def on_outside_update(self, dummy):
        for var in self.node_tree.sn_variables:
            for my_var in self.var_collection:
                if my_var.new_identifier:
                    if my_var.new_identifier == var.identifier:
                        my_var.name = var.name
        for prop in self.node_tree.sn_properties:
            for my_prop in self.prop_collection:
                if my_prop.new_identifier:
                    if my_prop.new_identifier == prop.identifier:
                        my_prop.name = prop.name


        for prop in self.prop_collection:
            prop.update_name(None)
        for var in self.var_collection:
            var.update_name(None)

    def get_function_definitions(self):
        if ".json" in self.snippet_path:
            with open(self.snippet_path) as snippet:
                data = json.loads(snippet.read())
                if "function_definitions" in data:
                    return data["function_definitions"]
        return {}


    def update_snippet(self, context):
        self.var_collection.clear()
        self.prop_collection.clear()
        self.inputs.clear()
        self.outputs.clear()
        self.has_vars = False

        if self.snippet_path:
            if not self.snippet_path == bpy.path.abspath(self.snippet_path):
                self.snippet_path = bpy.path.abspath(self.snippet_path)
            else:

                if ".json" in self.snippet_path:
                    with open(self.snippet_path) as snippet:
                        data = json.loads(snippet.read())
                        self.label = data["name"]

                        if "property_identifiers" in data and len(data["property_identifiers"]):
                            self.has_vars = True
                        elif "SNIPPET_VARS" in data["function"]:
                            if len(data["function"].split("}")[0].split("{")[-1]):
                                self.has_vars = True

                        if "property_identifiers" in data:
                            for prop in data["property_identifiers"]:
                                new_prop = self.prop_collection.add()
                                new_prop.is_prop = True
                                new_prop.node_uid = self.uid
                                new_prop.og_name = data["property_identifiers"][prop][0]
                                new_prop.type = data["property_identifiers"][prop][1]
                                new_prop.identifier = prop
                                new_prop.attach_property_to = data["property_identifiers"][prop][2]

                        if "variable_definitions" in data:
                            for var in data["variable_definitions"]:
                                new_var = self.var_collection.add()
                                new_var.node_uid = self.uid
                                new_var.og_name = data["variable_definitions"][var][0]
                                new_var.type = data["variable_definitions"][var][1]
                                new_var.identifier = var

                        for inp_data in data["inputs"]:
                            if inp_data["idname"] == "SN_ExecuteSocket": inp_data["name"] = "Execute"
                            if inp_data["idname"] == "SN_InterfaceSocket": inp_data["name"] = "Interface"
                            inp = self.add_input(inp_data["idname"], inp_data["name"])
                            inp.subtype = inp_data["subtype"]

                            if "attributes" in inp_data:
                                for attr in inp_data["attributes"]:
                                    setattr(inp, attr, inp_data["attributes"][attr])

                        for out_data in data["outputs"]:
                            if out_data["idname"] == "SN_ExecuteSocket": out_data["name"] = "Execute"
                            if out_data["idname"] == "SN_InterfaceSocket": out_data["name"] = "Interface"
                            out = self.add_output(out_data["idname"], out_data["name"])
                            out.subtype = out_data["subtype"]

                            if "attributes" in out_data:
                                for attr in out_data["attributes"]:
                                    setattr(out, attr, out_data["attributes"][attr])
        
        self.auto_compile()


    snippet_path: bpy.props.StringProperty(subtype="FILE_PATH",name="Path",description="Path to the snippet json file", update=update_snippet)
    has_vars: bpy.props.BoolProperty(default=False)
    var_collection: bpy.props.CollectionProperty(type=SN_VarPropertyGroup)
    prop_collection: bpy.props.CollectionProperty(type=SN_VarPropertyGroup)


    def get_variables(self):
        if ".json" in self.snippet_path:
            with open(self.snippet_path) as snippet:
                data = json.loads(snippet.read())
                if "variable_definitions" in data:
                    return data["variable_definitions"]
        return {}


    def on_create(self,context):
        self.label = "Snippet"


    def draw_node(self,context,layout):
        if self.label == "Snippet":
            layout.prop(self,"snippet_path")

        for var in self.var_collection:
            row = layout.row(align=True)
            row.label(text=var.og_name+":")
            row.prop_search(var, "name", self.node_tree, "sn_variables", text="")
            row.operator("sn.question_mark", text="", icon="QUESTION").to_display = "Choose a '" + var.type.replace("_", " ").title() + "' variable to assign this snippet variable to.\nIf you don't choose anything it will use the snippets standalone variable."

        for prop in self.prop_collection:
            row = layout.row(align=True)
            row.label(text=prop.og_name+":")
            row.prop_search(prop, "name", self.node_tree, "sn_properties", text="")
            row.operator("sn.question_mark", text="", icon="QUESTION").to_display = "Choose a '" + prop.type.replace("_", " ").title() + "' property to assign this snippet property to.\nIf you don't choose anything it will use the snippets standalone property."


    def get_main_function(self):
        if ".json" in self.snippet_path:
            code = ["\n\n"]
            with open(self.snippet_path) as snippet:
                data = json.loads(snippet.read())
                data["function"] = data["function"].replace(data["func_name"],self.func_name(data["func_name"]))
            return data["function"] + "\n"
        return ""

    def get_property_identifiers(self):
        if ".json" in self.snippet_path:
            code = []
            with open(self.snippet_path) as snippet:
                data = json.loads(snippet.read())
                if "property_identifiers" in data:
                    return data["property_identifiers"]
        return []

    def func_name(self, orginal_name):
        return orginal_name + "_snippet_" + self.uid


    def get_reg_unreg_code(self, name):
        with open(self.snippet_path) as snippet:
            data = json.loads(snippet.read())
            if name in data:
                used_props = []
                for prop in self.prop_collection:
                    if prop.name in self.node_tree.sn_properties and prop.type == self.node_tree.sn_properties[prop.name].var_type and prop.attach_property_to == self.node_tree.sn_properties[prop.name].attach_property_to:
                        used_props.append(prop.identifier)
                
                code = "\n"
                for line in data[name].split("\n"):
                    if "property_identifiers" in data:
                        for prop in data["property_identifiers"]:
                            if prop in line and not prop in used_props:
                                code += line.replace(prop, prop + "_" + self.uid)+"\n"

                return {"code": code}


    def code_register(self, context):
        if os.path.exists(self.snippet_path):
            return self.get_reg_unreg_code("register")
        return {"code": ""}


    def code_unregister(self, context):
        if os.path.exists(self.snippet_path):
            return self.get_reg_unreg_code("unregister")
        return {"code": ""}


    def code_imperative(self, context):
        if os.path.exists(self.snippet_path):
            # set identifier for non selected variables
            var_id = f"snippet_vars_{self.uid}"

            # write strings for processing
            var_identifier = self.get_main_function().split("\n")[0].strip().replace("SNIPPET_VARS", var_id)
            identifier = self.get_main_function().split("\n")[1].strip()
            code = ""
            for function in self.get_function_definitions():
                code += self.get_function_definitions()[function]
            main_code = "\n".join(self.get_main_function().split("\n")[2:])


            # replace var names with selected
            for var in self.var_collection:
                if var.name in self.node_tree.sn_variables and var.type == self.node_tree.sn_variables[var.name].var_type:
                    code = code.replace('SNIPPET_VARS["' + var.identifier, self.get_python_name(self.node_tree.name) + '["' + self.node_tree.sn_variables[var.name].identifier)
                    main_code = main_code.replace('SNIPPET_VARS["' + var.identifier, self.get_python_name(self.node_tree.name) + '["' + self.node_tree.sn_variables[var.name].identifier)

            # replace not selected vars with standalone
            code = code.replace("SNIPPET_VARS", var_id)
            main_code = main_code.replace("SNIPPET_VARS", var_id)

            # replace property identifiers
            for prop in self.prop_collection:
                code = code.replace(prop.identifier, prop.identifier+"_unused")
                main_code = main_code.replace(prop.identifier, prop.identifier+"_unused")
            for prop in self.prop_collection:
                if prop.name in self.node_tree.sn_properties and prop.type == self.node_tree.sn_properties[prop.name].var_type and prop.attach_property_to == self.node_tree.sn_properties[prop.name].attach_property_to:
                    code = code.replace(prop.identifier+"_unused", self.node_tree.sn_properties[prop.name].identifier)
                    main_code = main_code.replace(prop.identifier+"_unused", self.node_tree.sn_properties[prop.name].identifier)
                else:
                    code = code.replace(prop.identifier+"_unused", prop.identifier + "_" + self.uid)
                    main_code = main_code.replace(prop.identifier+"_unused", prop.identifier + "_" + self.uid)


            # split strings for list processing
            code = code.split("\n")
            for i in range(len(code)): 
                code[i] = code[i] + "\n"
            main_code = main_code.split("\n")
            for i in range(len(main_code)): 
                main_code[i] = main_code[i] + "\n"

            return {
                "code": f"""
                        {var_identifier}
                        {identifier}
                            {self.list_code(code, 7)}
                            {self.list_code(main_code, 7)}
                        """
            }
        return {"code": ""}


    def code_evaluate(self, context, touched_socket):
        if os.path.exists(self.snippet_path):
            func_name = ""
            with open(self.snippet_path) as snippet:
                data = json.loads(snippet.read())
                func_name = self.func_name(data["func_name"])

            parameters = []
            
            if len(self.inputs) > 0 and self.inputs[0].bl_idname == "SN_InterfaceSocket":
                layout = touched_socket.links[0].from_node.what_layout(touched_socket.links[0].from_socket)
                parameters.append(layout + ", ")
            
            for inp in self.inputs:
                if not inp.bl_idname in ["SN_ExecuteSocket", "SN_InterfaceSocket"]:
                    parameters.append(inp.code() + ", ")

            if len(self.inputs) > 0 and touched_socket == self.inputs[0]:
                return {
                    "code": f"""
                            snippet_return_{self.uid} = {func_name}({self.list_code(parameters)})
                            {self.outputs[0].code(7) if len(self.outputs) else ""}
                            """
                }

            else:
                return {
                    "code": f"""{func_name}({self.list_code(parameters)})[{self.outputs.find(touched_socket.name)-1}]"""
                }

        self.add_error("No snippet file", "This snippet file does not exist!", True)
        return {"code": ""}
