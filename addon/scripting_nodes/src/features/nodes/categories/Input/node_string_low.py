from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_StringCase(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_StringCase"
    bl_label = "String Case"

    def update_value(self, context):
        self._generate()

    string_case: bpy.props.EnumProperty(
        name="string_case",
        description="Select a string transformation mode",
        items=[
            ("LOWER", "Lowercase", "Convert to lowercase"),
            ("UPPER", "Uppercase", "Convert to uppercase"),
            ("CAMEL", "Camel Case", "Convert to camel case"),
        ],
        default="LOWER",
        update=update_value,
    )

    def draw(self, context, layout):
        layout.prop(self, "string_case", text="Case")

    def on_create(self):
        self.add_input("ScriptingStringSocket")
        self.add_output("ScriptingStringSocket")


    def generate(self):
        # Create the transformation code based on selected case
        if self.string_case == "LOWER":
            print("Lower")
            self.outputs[0].code = self.inputs[0].eval().lower()
        elif self.string_case == "UPPER":
            print("Upper")
            self.outputs[0].code = self.inputs[0].eval().upper()
        elif self.string_case == "CAMEL":
            print("Camel")
            self.outputs[0].code = f"''.join(word.capitalize() for word in {self.inputs[0].eval()}.split())"
