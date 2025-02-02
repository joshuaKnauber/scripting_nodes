from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Float(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Float"
    bl_label = "Float"

    def update_value(self, context):
        self._generate()

    value: bpy.props.FloatProperty(default=1, update=update_value)

    def draw(self, context, layout):
        layout.prop(self, "value", text="")

    def on_create(self):
        self.add_output("ScriptingFloatSocket")

    def generate(self):
        self.outputs[0].code = f"{self.value}"
