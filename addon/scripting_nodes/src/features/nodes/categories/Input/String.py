from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_String(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_String"
    bl_label = "String"

    def update_value(self, context):
        self._generate()

    value: bpy.props.StringProperty(default="", update=update_value)

    def draw(self, context, layout):
        layout.prop(self, "value", text="", placeholder="Value")

    def on_create(self):
        self.add_output("ScriptingStringSocket")

    def generate(self):
        self.outputs[0].code = f'"{self.value}"'
