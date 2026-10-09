import bpy

from ....core import naming
from ....sockets.spec import Interface, String
from ...base_node import ScriptingBaseNode


class SNA_Node_Menu(ScriptingBaseNode, bpy.types.Node):
    """A dropdown menu button. Its contents are drawn into a Menu class."""

    bl_idname = "SNA_Node_Menu"
    bl_label = "Menu"
    sn_inputs = [Interface(), String("label", "Label", default="Menu")]
    sn_outputs = [Interface("content", "Menu"), Interface("next", "After")]

    def sn_names(self):
        return [naming.Class("class", "MT", naming.label(self))]

    def emit(self, ctx):
        menu = ctx.name("class")
        label = ctx.input("label")
        ctx.module(f"""
            class {menu}(bpy.types.Menu):
                bl_idname = {menu!r}
                bl_label = {label}

                def draw(self, context):
                    {ctx.flow("content", layout="self.layout")}
        """)
        ctx.code(f"""
            {ctx.layout}.menu({menu!r}, text={label})
            {ctx.flow("next")}
        """)
