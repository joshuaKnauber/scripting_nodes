import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_StringNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_StringNode"
    bl_label = "String"
    node_color = "STRING"

    def on_create(self, context):
        self.add_string_output("String")

    def evaluate(self, context):
        self.outputs["String"].python_value = f"\"{self.string}\""

    string: bpy.props.StringProperty(name="String", description="String value of this node", update=evaluate)

    def draw_node(self, context, layout):
        layout.prop(self, "string", text="")