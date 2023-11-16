import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_ReadTextFileNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_ReadTextFileNode"
    bl_label = "Read Text File"
    bl_width_default = 200
    node_color = "PROGRAM"
    
    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.add_string_input("Path").subtype = "FILE_PATH"
        self.add_string_output("Text")
        self.add_list_output("Lines")

    def evaluate(self, context):
        path = self.inputs["Path"].python_value

        self.code_import = "import os"
        self.code = f"""
                    text_{self.static_uid} = ""
                    lines_{self.static_uid} = []
                    if os.path.exists({path}):
                        with open({path}, "r") as file_{self.static_uid}:
                            lines_{self.static_uid} = list(map(lambda l: l.strip(), file_{self.static_uid}.readlines()))
                            text_{self.static_uid} = "\\n".join(lines_{self.static_uid})
                    {self.indent(self.outputs[0].python_value, 5)}
                    """

        self.outputs["Text"].python_value = f"text_{self.static_uid}"
        self.outputs["Lines"].python_value = f"lines_{self.static_uid}"