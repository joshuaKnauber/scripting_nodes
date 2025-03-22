from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Replace_In_String(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Replace_In_String"
    bl_label = "Replace in String"
    bl_description = "Replace a certain sign, word, or character in a string with another, or remove it by leaving the new field empty"
    bl_width_default = 200

    def on_create(self):
        self.add_input("ScriptingBooleanSocket", label="Case Sensitive")
        self.add_input("ScriptingStringSocket", label="String")
        self.add_input("ScriptingStringSocket", label="Old")
        self.add_input("ScriptingStringSocket", label="New")
        self.add_output("ScriptingStringSocket",label="String")

    def generate(self):
        self.code_global = "import re"
        self.outputs[0].code = f"{self.inputs[1].eval()}.replace({self.inputs[2].eval()}, {self.inputs[3].eval()}) if {self.inputs[0].eval()} else re.sub({self.inputs[2].eval()}, {self.inputs[3].eval()}, {self.inputs[1].eval()}, flags=re.IGNORECASE)"
