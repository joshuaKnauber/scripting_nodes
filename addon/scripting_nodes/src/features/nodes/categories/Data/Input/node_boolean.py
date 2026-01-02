from ....base_node import ScriptingBaseNode
import bpy


class SNA_Node_Boolean(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Boolean"
    bl_label = "Boolean"

    def update_value(self, context):
        self._generate()

    value: bpy.props.BoolProperty(default=True, update=update_value)

    def draw(self, context, layout):
        layout.prop(self, "value", text="Value")

    def on_create(self):
        self.add_output("ScriptingBooleanSocket")

    def generate(self):
        self.outputs[0].code = f"{self.value}"
