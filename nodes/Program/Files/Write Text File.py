import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_WriteTextFileNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_WriteTextFileNode"
    bl_label = "Write Text File"
    bl_width_default = 200
    node_color = "PROGRAM"
    
    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.add_string_input("Path").subtype = "FILE_PATH"
        self.add_string_input("Text")
        
    write_type: bpy.props.EnumProperty(name="Type",
                            description="Where to write to in the text file",
                            items=[("APPEND", "Append", "Append text to the end of the file"),
                                   ("OVERWRITE", "Overwrite", "Overwrite the content of the file")],
                            default="APPEND",
                            update=SN_ScriptingBaseNode._evaluate)

    def draw_node(self, context, layout):
        layout.prop(self, "write_type", expand=True)

    def evaluate(self, context):
        path = self.inputs["Path"].python_value
        
        self.code_import = "import os"

        if self.write_type == "APPEND":
            self.code = f"""
                        with open({path}, mode='a') as file_{self.static_uid}:
                            {f"file_{self.static_uid}.seek(0)" if self.write_type == "OVERWRITE" else ""}
                            file_{self.static_uid}.write({self.inputs["Text"].python_value})
                            {f"file_{self.static_uid}.truncate()" if self.write_type == "OVERWRITE" else ""}
                        {self.indent(self.outputs[0].python_value, 6)}
                        """
        else:
            self.code = f"""
                        with open({path}, mode='w') as file_{self.static_uid}:
                            file_{self.static_uid}.seek(0)
                            file_{self.static_uid}.write({self.inputs["Text"].python_value})
                            file_{self.static_uid}.truncate()
                        {self.indent(self.outputs[0].python_value, 6)}
                        """