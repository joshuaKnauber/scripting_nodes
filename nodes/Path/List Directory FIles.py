import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_ListDirectoryFilesNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ListDirectoryFilesNode"
    bl_label = "List Directory Files"
    node_color = "STRING"

    def on_create(self, context):
        self.add_string_input("Path").subtype = "FILE_PATH"
        self.add_list_output("Files + Directories")
        self.add_list_output("Files")
        self.add_list_output("Directories")
        
    with_root: bpy.props.BoolProperty(name="With Path",
                            description="Returns a list of full paths instead of just the file and directory names",
                            default=True, update=SN_ScriptingBaseNode._evaluate)

    def draw_node(self, context, layout):
        layout.prop(self, "with_root")

    def evaluate(self, context):
        self.code_import = "import os"
        
        if not self.with_root:
            self.outputs[0].python_value = f"os.listdir({self.inputs['Path'].python_value})"
            if len(self.outputs) > 1:
                self.outputs[1].python_value = f"[f for f in os.listdir({self.inputs['Path'].python_value}) if os.path.isfile(os.path.join({self.inputs['Path'].python_value}, f))]"
                self.outputs[2].python_value = f"[f for f in os.listdir({self.inputs['Path'].python_value}) if os.path.isdir(os.path.join({self.inputs['Path'].python_value}, f))]"
        
        else:
            self.outputs[0].python_value = f"[os.path.join({self.inputs['Path'].python_value}, f) for f in os.listdir({self.inputs['Path'].python_value})]"
            if len(self.outputs) > 1:
                self.outputs[1].python_value = f"[os.path.join({self.inputs['Path'].python_value}, f) for f in os.listdir({self.inputs['Path'].python_value}) if os.path.isfile(os.path.join({self.inputs['Path'].python_value}, f))]"
                self.outputs[2].python_value = f"[os.path.join({self.inputs['Path'].python_value}, f) for f in os.listdir({self.inputs['Path'].python_value}) if os.path.isdir(os.path.join({self.inputs['Path'].python_value}, f))]"
