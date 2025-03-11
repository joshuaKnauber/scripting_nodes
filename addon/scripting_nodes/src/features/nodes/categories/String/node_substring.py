from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Substring(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Substring"
    bl_label = "Substring In String"

    def update_data_type(self, context):
        self._generate()

    case_sensitive: bpy.props.BoolProperty(
        name="Case Sensitive",
        default=True,
        update=update_data_type,
    )

    def on_create(self):
        self.add_input("ScriptingStringSocket", "String")
        self.add_input("ScriptingStringSocket", "Substring")
        self.add_output("ScriptingBooleanSocket", "Is in String")

    def draw(self, context, layout):
        layout.prop(self, "case_sensitive", text="Case Sensitive")

    def generate(self):
        string1 = self.inputs["String"].eval()
        string2 = self.inputs["Substring"].eval()

        if not self.case_sensitive:
            self.outputs[0].code = f"{string2} in {string1}"
        else:
            self.outputs[0].code = f"{string2}.lower() in {string1}.lower()"
