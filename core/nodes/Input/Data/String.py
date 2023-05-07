import bpy
from ...base_node import SN_BaseNode
from .....utils.codify import codify_string_value


class SN_StringNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_StringNode"
    bl_label = "String"

    value: bpy.props.StringProperty(
        default="", update=SN_BaseNode._update)

    def on_create(self, context):
        self.add_string_output()

    def draw_node(self, context, layout):
        layout.prop(self, "value", text="")

    def generate(self, context):
        self.outputs[0].code = codify_string_value(self.value)
