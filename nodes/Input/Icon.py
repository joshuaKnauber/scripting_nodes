import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_IconNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IconNode"
    bl_label = "Icon"
    node_color = "ICON"

    def on_create(self, context):
        self.add_icon_output("Icon")

    def evaluate(self, context):
        self.outputs["Icon"].python_value = f"{self.icon}"

    icon: bpy.props.IntProperty(name="Value", description="Value of this socket", update=evaluate)

    def draw_node(self, context, layout):
        op = layout.operator("sn.select_icon", text="Choose Icon", icon_value=self.icon)
        op.node = self.name
        op.socket = -1

