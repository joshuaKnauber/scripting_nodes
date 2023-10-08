import bpy

from ....constants import sockets
from ..base_node import SN_BaseNode


class SN_BoolPropertyNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_BoolPropertyNode"
    bl_label = "Boolean Property"

    def on_create(self):
        self.name = "New Boolean"
        self.add_input(sockets.PROPERTY, "Source")
        self.add_output(sockets.EXECUTE, "On Update")
        self.add_output(sockets.PROPERTY, "Boolean Property")
        self.add_output(sockets.BOOLEAN, "Boolean Value")

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        row = layout.row()
        row.prop(self, "name", text="")
        row.operator("sn.node_settings", text="", icon="PREFERENCES", emboss=False).node = self.name

    def generate(self, context):
        self.require_register = True

        prop_identifier = f"prop_{self.id}"

        self.outputs["Boolean Property"].code = f"bpy.context.scene.{prop_identifier}"
        self.outputs["Boolean Property"].set_meta("data", "bpy.context.scene")
        self.outputs["Boolean Property"].set_meta("identifier", prop_identifier)

        self.outputs["Boolean Value"].code = f"bpy.context.scene.{prop_identifier}"

        self.code_register = f"bpy.types.Scene.{prop_identifier} = bpy.props.BoolProperty(name='{self.name}')"
        self.code_unregister = f"del bpy.types.Scene.{prop_identifier}"
