from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Replace_In_String(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Replace_In_String"
    bl_label = "Replace in String"
    bl_width_default = 200

    def on_create(self):
        self.add_input("ScriptingBooleanSocket", label="Ignore Case Sensitivity")
        self.add_input("ScriptingStringSocket", label="String")
        self.add_input("ScriptingStringSocket", label="Old")
        self.add_input("ScriptingStringSocket", label="New")
        self.add_output("ScriptingStringSocket",label="String")
        self.inputs[0].value = False

    def generate(self):
        self.code_global = "import re"
        ignore_case = self.inputs[0].eval() 
        string = self.inputs[1].eval()
        old = self.inputs[2].eval()
        new = self.inputs[3].eval()
        self.outputs[0].code = f"re.sub({old}, {new}, {string}, flags=re.IGNORECASE) if {ignore_case} else {string}.replace({old}, {new})"
