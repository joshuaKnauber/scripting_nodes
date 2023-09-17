import bpy

from ....constants import sockets
from ..base_node import SN_BaseNode


class SN_BoolPropertyNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_BoolPropertyNode"
    bl_label = "Boolean Property"

    name: bpy.props.StringProperty(name="Name", default="New Property", update=lambda self, context: self.mark_dirty())

    def on_create(self):
        self.add_output(sockets.EXECUTE, "On Update")
        self.add_output(sockets.PROPERTY, "Updated Property")
        self.add_output(sockets.BOOLEAN, "Updated Property Value")

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        layout.prop(self, "name", text="")

    def generate(self, context):
        self.require_register = True

        # self.outputs["Value"].
        self.code_register = f"bpy.types.Scene.prop_{self.id} = bpy.props.BoolProperty(name='{self.name}')"
        self.code_unregister = f"del bpy.types.Scene.prop_{self.id}"
