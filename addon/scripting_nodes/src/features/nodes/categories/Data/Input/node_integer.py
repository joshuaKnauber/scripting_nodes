from ....base_node import ScriptingBaseNode
import bpy


class SNA_Node_Integer(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Integer"
    bl_label = "Integer"

    def update_value(self, context):
        self._generate()

    value: bpy.props.IntProperty(default=1, update=update_value)

    def draw(self, context, layout):
        layout.prop(self, "value", text="")

    def on_create(self):
        self.add_output("ScriptingIntegerSocket")

    def generate(self):
        self.outputs[0].code = f"{self.value}"
