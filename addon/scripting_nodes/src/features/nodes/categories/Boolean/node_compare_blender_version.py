from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Compare_Blender_Version(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Compare_Blender_Version"
    bl_label = "Compare Blender Version"
    bl_description = "Checks if the Blender version being used is equal to, greater than, or less than a specified version"

    def update_value(self, context):
        self._generate()

    def update_comparison(self, context):
        self._generate()

    def on_create(self):
        self.add_input("ScriptingStringSocket", label="to")
        self.add_output("ScriptingBooleanSocket", label="Result")

    comparison_types = [
        ("==", "=", "Equal to"),
        ("!=", "≠", "Not equal to"),
        ("<", "<", "Less than"),
        ("<=", "≤", "Less than or equal to"),
        (">", ">", "Greater than"),
        (">=", "≥", "Greater than or equal to"),
    ]
    comparison_type: bpy.props.EnumProperty(
        items=comparison_types, name="Comparison Type", update=update_comparison
    )

    value: bpy.props.StringProperty(
        default="", update=update_value, options={"TEXTEDIT_UPDATE"}
    )

    def draw(self, context, layout):
        column = layout.column()
        column.label(text="Used Version:")
        layout.prop(self, "comparison_type", text="")

    def generate(self):
        self.outputs[0].code = (
            f'"{bpy.app.version_string}" {self.comparison_type} {str(self.inputs[0].eval())}'
        )
