from ....base_node import ScriptingBaseNode
import bpy


class SNA_Node_BooleanMath(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_BooleanMath"
    bl_label = "Boolean Math"

    def update_data_type(self, context):
        self._generate()

    comparison: bpy.props.EnumProperty(
        items=[
            ("AND", "And", ""),
            ("OR", "Or", ""),
        ],
        name="Comparison",
        default="AND",
        update=update_data_type,
    )

    def on_create(self):
        self.add_input("ScriptingBooleanSocket", "Boolean")
        self.add_input("ScriptingBooleanSocket", "Boolean")
        self.add_output("ScriptingBooleanSocket", "Result")

    def draw(self, context, layout):
        layout.prop(self, "comparison", text="")

    def generate(self):
        value1 = self.inputs["Boolean"].eval()
        value2 = self.inputs["Boolean"].eval()

        self.outputs["Result"].code = f"{value1} {self.comparison.lower()} {value2}"
