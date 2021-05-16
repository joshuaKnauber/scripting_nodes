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
        return node.addon_tree.sn_nodes["SN_FunctionNode"].items[node.func_name].node()

    def get_snippet(self, context):
        run_node = context.space_data.node_tree.nodes.active
        node = self.function_node(context)
        data = {"name":node.func_name ,"function":"", "func_name":node.item.identifier, "inputs":[], "outputs":[]}

        for inp in run_node.inputs:
            data["inputs"].append({"idname":inp.bl_idname, "name":inp.get_text(), "subtype":inp.subtype})

        for out in run_node.outputs:
            data["outputs"].append({"idname":out.bl_idname, "name":out.get_text(), "subtype":out.subtype})

        data["function"] = node.code_imperative(context)["code"]

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
                            inp = self.add_input(inp_data["idname"], inp_data["name"])
                            inp.subtype = inp_data["subtype"]

                        for out_data in data["outputs"]:
                            if out_data["idname"] == "SN_ExecuteSocket": out_data["name"] = "Execute"
                            out = self.add_output(out_data["idname"], out_data["name"])
                            out.subtype = out_data["subtype"]


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
                code += data["function"].split("\n")
                for i in range(len(code)): 
                    code[i] = code[i] + "\n"
                
            return {
                "code": f"""
                        {self.list_code(code)}
                        """
            }


    def code_evaluate(self, context, touched_socket):
        if len(self.inputs) > 0:
            func_name = ""
            with open(self.snippet_path) as snippet:
                data = json.loads(snippet.read())
                func_name = self.func_name(data["func_name"])

            parameters = []
            for inp in self.inputs[1:]:
                parameters.append(inp.code() + ", ")

            if touched_socket == self.inputs[0]:
                return {
                    "code": f"""
                            snippet_return_{self.uid} = {func_name}({self.list_code(parameters)})
                            {self.outputs[0].code(7)}
                            """
                }

            elif self.inputs[0].is_linked:
                return {
                    "code": f"""snippet_return_{self.uid}[{self.outputs.find(touched_socket.name)-1}]"""
                }
            else:
                self.add_error("Snippet not run", "You need to execute your snippet to use an output value")
                return {"code": "None"}

        else:
            return {
                "code": f"""
                        {self.outputs[0].code(6)}
                        """
            }