import bpy
import os
import json

from ...utils import normalize_code
from ..base_node import SN_ScriptingBaseNode



class SN_SnippetNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SnippetNode"
    bl_label = "Snippet"
    node_color = "STRING"
    bl_width_default = 200

    def setup_snippet_node(self, data):
        self.label = data["name"]
        # setup inputs
        for inp in data["inputs"]:
            socket = self._add_input(inp["idname"], inp["name"])
            socket.subtype = inp["subtype"]
            for attr in inp["attributes"].keys():
                setattr(socket, attr, inp["attributes"][attr])
        # setup outputs
        for out in data["outputs"]:
            socket = self._add_output(out["idname"], out["name"])
            socket.subtype = out["subtype"]
            for attr in out["attributes"].keys():
                setattr(socket, attr, out["attributes"][attr])

    def update_snippet_to_3(self, data):
        # set execute socket name
        for inp in data["inputs"]:
            if inp["idname"] == "SN_ExecuteSocket":
                inp["name"] = "Execute"
        for out in data["outputs"]:
            if out["idname"] == "SN_ExecuteSocket":
                out["name"] = "Execute"
        return data
    
    def load_snippet_file(self, path):
        with open(path, "r") as snippet_file:
            snippet = json.loads(snippet_file.read())
            snippet = self.update_snippet_to_3(snippet)
            self.setup_snippet_node(snippet)
            self.data = json.dumps(snippet)

    def update_snippet_path(self, context):
        if not self.path == bpy.path.abspath(self.path):
            self["path"] = bpy.path.abspath(self.path)
        if os.path.exists(self.path):
            self.load_snippet_file(self.path)

    data: bpy.props.StringProperty(name="Data",
                                description="The data loaded from the last snippet file",
                                update=SN_ScriptingBaseNode._evaluate)

    path: bpy.props.StringProperty(name="Path", subtype="FILE_PATH",
                                description="The path to the snippet json file",
                                update=update_snippet_path)

    def evaluate(self, context):
        if self.data:
            snippet = json.loads(self.data)
            
            code = "\n" + normalize_code(snippet["function"])
            code = code.replace("SNIPPET_VARS", f"vars_{self.static_uid}")
            code = code.replace(snippet["func_name"], snippet["func_name"]+"_"+self.static_uid)
            code = code + "\n" + snippet["code_imperative"] + "\n"
            self.code_imperative = code
            
            self.code_register = snippet["register"]
            self.code_unregister = snippet["unregister"]
    
    def draw_node(self, context, layout):
        layout.label(text="WIP", icon="ERROR")
        if not self.data:
            layout.prop(self, "path")