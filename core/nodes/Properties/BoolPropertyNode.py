import bpy

from ....constants import sockets
from ..base_node import SN_BaseNode


class SN_BoolPropertyNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_BoolPropertyNode"
    bl_label = "Boolean Property"

    prop_name: bpy.props.StringProperty(name="Name", default="New Property", update=lambda self, context: self.mark_dirty())

    def on_create(self):
        self.add_output(sockets.EXECUTE, "On Update")
        self.add_output(sockets.PROPERTY, "Boolean Property")
        self.add_output(sockets.BOOLEAN, "Boolean Value")

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        row = layout.row()
        row.prop(self, "prop_name", text="")
        row.operator("sn.node_settings", text="", icon="PREFERENCES", emboss=False).node = self.name

    def generate(self, context):
        self.require_register = True

        # self.outputs["Value"].
        self.code_register = f"bpy.types.Scene.prop_{self.id} = bpy.props.BoolProperty(name='{self.name}')"
        self.code_unregister = f"del bpy.types.Scene.prop_{self.id}"
