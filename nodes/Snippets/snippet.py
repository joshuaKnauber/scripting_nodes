import bpy
import json
import os
from ...node_tree.base_node import SN_ScriptingBaseNode



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
        for node in list(set(self.get_all_connected(start_node, []))):
            if node.bl_idname in ["SN_GetVariableNode", "SN_SetVariableNode", "SN_ChangeVariableNode", "SN_ResetVariableNode", "SN_AddToListNode", "SN_RemoveFromListNode"]:
                if node.search_value in node.node_tree.sn_variables:
                    vars.append(node.search_value)
        return vars
    
    def get_used_properties(self, start_node):
        props = []
        for node in list(set(self.get_all_connected(start_node, []))):
            if node.bl_idname in ["SN_GetPropertyNode"]:
                if node.prop_name in node.node_tree.sn_properties:
                    props.append(node.node_tree.sn_properties[node.prop_name])
        return props

    def get_variable_code(self, node):
        used_variables = list(set(self.get_used_variables(node)))
        code = ""
        for var in used_variables:
            code += node.node_tree.sn_variables[var].variable_register()
        return "snippet_vars = {" + code + "}"
    
    def get_prop_register(self, props):
        code = "\n"
        for prop in props:
            code += prop.property_register()
        return code
    
    def get_prop_unregister(self, props):
        code = "\n"
        for prop in props:
            code += prop.property_unregister()
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
        data = { "name":node.func_name,
                "function":"", "register":"", "unregister":"", "properties":[],
                "func_name":node.item.identifier,
                "inputs":[], "outputs":[] }

        for inp in run_node.inputs:
            data["inputs"].append({"idname":inp.bl_idname, "name":inp.get_text(), "subtype":inp.subtype, "attributes":self.get_socket_attributes(inp)})

        for out in run_node.outputs:
            data["outputs"].append({"idname":out.bl_idname, "name":out.get_text(), "subtype":out.subtype, "attributes":self.get_socket_attributes(inp)})

        # get function code
        code = node.code_imperative(context)["code"]

        # add variables
        code = code.split("\n")
        spaces = " " * (len(code[2]) - len(code[2].lstrip()))
        code.insert(2, spaces + self.get_variable_code(node))
        code = ("\n").join(code)
        
        # replace variable calls
        og_name = node.get_python_name(node.node_tree.name) + "["
        code = code.replace(og_name, "snippet_vars[")

        data["function"] = code
        
        props = list(set(self.get_used_properties(node)))
        data["register"] = self.get_prop_register(props)
        data["unregister"] = self.get_prop_unregister(props)
        data["property_identifiers"] = [prop.identifier for prop in props]

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



class SN_SnippetNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SnippetNode"
    bl_label = "Snippet"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3)
    }


    def update_snippet(self, context):
        self.inputs.clear()
        self.outputs.clear()

        if self.snippet_path:
            if not self.snippet_path == bpy.path.abspath(self.snippet_path):
                self.snippet_path = bpy.path.abspath(self.snippet_path)
            else:

                if ".json" in self.snippet_path:
                    with open(self.snippet_path) as snippet:
                        data = json.loads(snippet.read())
                        self.label = data["name"]

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


    snippet_path: bpy.props.StringProperty(subtype="FILE_PATH",name="Path",description="Path to the snippet json file", update=update_snippet)
    

    def on_create(self,context):
        self.label = "Snippet"


    def draw_node(self,context,layout):
        if self.label == "Snippet":
            layout.prop(self,"snippet_path")

    
    def func_name(self, orginal_name):
        return orginal_name + "_snippet_" + self.uid


    def code_imperative(self, context):
        if ".json" in self.snippet_path:
            code = [""]
            with open(self.snippet_path) as snippet:
                data = json.loads(snippet.read())
                data["function"] = data["function"].replace(data["func_name"],self.func_name(data["func_name"]))

                # update property names
                if "property_identifiers" in data:
                    for prop in data["property_identifiers"]:
                        data["function"] = data["function"].replace(prop, prop+"_"+self.uid)

                code += data["function"].split("\n")
                for i in range(len(code)): 
                    code[i] = code[i] + "\n"
                
            return {
                "code": f"""
                        {self.list_code(code)}
                        """
            }
            
            
    def get_reg_unreg_code(self, name):
        with open(self.snippet_path) as snippet:
            data = json.loads(snippet.read())
            if name in data:
                for prop in data["property_identifiers"]:
                    data[name] = data[name].replace(prop, prop+"_"+self.uid)
                return {"code": data[name]}
            
            
    def code_register(self, context):
        return self.get_reg_unreg_code("register")


    def code_unregister(self, context):
        return self.get_reg_unreg_code("unregister")


    def code_evaluate(self, context, touched_socket):
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
                        {self.outputs[0].code(6) if len(self.outputs) else ""}
                        """
            }

        else:
            return {
                "code": f"""{func_name}({self.list_code(parameters)})[{self.outputs.find(touched_socket.name)-1}]"""
            }