from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Replace_In_String(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Replace_In_String"
    bl_label = "Replace in String"
    bl_description = "Replace a certain sign, word, or character in a string with another, or remove it by leaving the new field empty"
    bl_width_default = 200

    def update_case_sensitive(self, context):
        self._generate()

    case_sensitive: bpy.props.BoolProperty(
        name="Case Sensitive", default=True, update=update_case_sensitive, description="Disable to ignore case sensitivity, meaning 'hello' as Old String will match 'HEllo' in 'HEllo World'."
    )

    def on_create(self):
        self.add_input("ScriptingStringSocket", label="String")
        self.add_input("ScriptingStringSocket", label="Old")
        self.add_input("ScriptingStringSocket", label="New")
        self.add_output("ScriptingStringSocket",label="String")

    def draw(self, context, layout):
        layout.prop(self, "case_sensitive", text="Case Sensitive")

    def generate(self):
        self.code_global = "import re"
        self.outputs[0].code = f"{self.inputs[0].eval()}.replace({self.inputs[1].eval()}, {self.inputs[2].eval()}) if {self.case_sensitive} else re.sub({self.inputs[1].eval()}, {self.inputs[2].eval()}, {self.inputs[0].eval()}, flags=re.IGNORECASE)"
