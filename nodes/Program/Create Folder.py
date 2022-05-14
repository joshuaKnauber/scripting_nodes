import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_CreateFolderNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CreateFolderNode"
    bl_label = "Create Folder"
    bl_width_default = 200
    node_color = "PROGRAM"
    
    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.add_string_input("Path").subtype = "DIR_PATH"
        self.add_string_input("Name").default_value = "New Folder"
        self.add_string_output("New Path").subtype = "DIR_PATH"

    def evaluate(self, context):
        path = self.inputs["Path"].python_value
        name = self.inputs["Name"].python_value

        self.outputs[1].python_value = ""
        self.code = f"""
                    {self.indent(self.outputs[0].python_value, 5)}
                    """

        if path and name:
            self.code_import = "import os"
            self.outputs[1].python_value = f"os.path.join({path},{name})" if path and name else ""
            self.code = f"""
                        if not os.path.exists(os.path.join({path},{name})):
                            os.mkdir(os.path.join({path},{name}))
                        {self.indent(self.outputs[0].python_value, 6)}
                        """