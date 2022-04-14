import bpy
import os
import json

from ...utils import normalize_code, get_python_name
from ..base_node import SN_ScriptingBaseNode



class SN_SnippetNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SnippetNode"
    bl_label = "Snippet"
    bl_width_default = 200

    def setup_snippet_node(self, data):
        """ This adds all in/outputs and settings to the snippet node """
        self.label = data["name"]
        for inp in data["inputs"]:
            socket = self._add_input(inp["idname"], inp["name"])
            if inp["subtype"] != "NONE":
                socket.subtype = inp["subtype"]
        for out in data["outputs"]:
            socket = self._add_output(out["idname"], out["name"])
            if out["subtype"] != "NONE":
                socket.subtype = out["subtype"]

    def load_snippet_file(self, path):
        with open(path, "r") as snippet_file:
            self.wrong_version = False
            snippet = json.loads(snippet_file.read())
            if "version" in snippet and snippet["version"] == 3:
                self.setup_snippet_node(snippet)
                self.data = json.dumps(snippet)
            else:
                self.wrong_version = True
                self.data = ""

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
    
    wrong_version: bpy.props.BoolProperty(default=False)

    def evaluate(self, context):
        if self.data:
            snippet = json.loads(self.data)

            self.code_import = snippet["import"]
            for var_tree in snippet["variables"]:
                self.code_imperative += var_tree.replace("SNIPPET_VARS", f"vars_{self.static_uid}") + " = {"
                for var in snippet["variables"][var_tree]:
                    self.code_imperative += "'" + var + "': " + snippet["variables"][var_tree][var] + ", "
                self.code_imperative += "}\n"
            for prop in snippet["properties"][0]:
                self.code_register += prop.replace("SNIPPET_VARS", f"vars_{self.static_uid}") + "\n"
            for prop in snippet["properties"][1]:
                self.code_unregister += prop.replace("SNIPPET_VARS", f"vars_{self.static_uid}") + "\n"

            self.code_register += snippet["register"].replace("SNIPPET_VARS", f"vars_{self.static_uid}")
            self.code_unregister += snippet["unregister"].replace("SNIPPET_VARS", f"vars_{self.static_uid}")

            code = "\n" + normalize_code(snippet["function"])
            code = code.replace(snippet["func_name"], snippet["func_name"]+"_"+self.static_uid)
            code = code + "\n" + snippet["imperative"] + "\n"
            code = code.replace("SNIPPET_VARS", f"vars_{self.static_uid}")
            self.code_imperative += code

            index = 1 if len(self.inputs) and self.inputs[0].bl_idname in ["SN_InterfaceSocket", "SN_ExecuteSocket"] else 0
            if len(self.inputs) and self.inputs[0].bl_idname == "SN_InterfaceSocket":
                inp_values = []
                for inp in self.inputs[1:]:
                    inp_values.append(inp.python_value)
                inp_values = ", ".join(inp_values)

                self.code = f"""
                            layout_function = {self.active_layout}
                            {snippet['func_name']}_{self.static_uid}(layout_function,{inp_values})
                            """

            else:
                inp_values = []
                for inp in self.inputs[index:]:
                    inp_values.append(inp.python_value)
                inp_values = ", ".join(inp_values)
                if len(self.inputs) and self.inputs[0].bl_idname == "SN_ExecuteSocket":
                    return_values = []
                    for i, out in enumerate(self.outputs[1:]):
                        return_values.append(get_python_name(f"{out.name}_{i}_{self.static_uid}", f"parameter_{i}_{self.static_uid}"))
                    return_names = ", ".join(return_values)

                    if return_names:
                        self.code = f"""
                                    {return_names} = {snippet['func_name']}_{self.static_uid}({inp_values})
                                    {self.indent(self.outputs[0].python_value, 9)}
                                    """
                    else:
                        self.code = f"""
                                    {snippet['func_name']}_{self.static_uid}({inp_values})
                                    {self.indent(self.outputs[0].python_value, 9)}
                                    """
                    for i, out in enumerate(self.outputs[1:]):
                        out.python_value = return_values[i]
                else:
                    if len(self.outputs) > 1:
                        for i, out in enumerate(self.outputs):
                            out.python_value = f"{snippet['func_name']}_{self.static_uid}({inp_values})[{i}]"
                    elif len(self.outputs) == 1:
                        self.outputs[-1].python_value = f"{snippet['func_name']}_{self.static_uid}({inp_values})"


    def draw_node(self, context, layout):
        if self.wrong_version:
            row = layout.row()
            row.alert = True
            row.label(text="You need to select a snippet that was created using Serpens 3!")
        if not self.data:
            layout.prop(self, "path")