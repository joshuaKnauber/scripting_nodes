import bpy

from ....core import naming
from ....sockets.spec import Icon, Interface, String
from ..._icon import icon_argument
from ...base_node import ScriptingBaseNode


class SNA_Node_Menu(ScriptingBaseNode, bpy.types.Node):
    """A dropdown menu button. Its contents are drawn into a Menu class."""

    bl_idname = "SNA_Node_Menu"
    bl_label = "Menu"
    sn_inputs = [Interface(), String("label", "Label", default="Menu"), Icon()]
    sn_outputs = [Interface("content", "Menu"), Interface("next", "After")]

    def sn_names(self):
        return [naming.Class("class", "MT", naming.label(self))]

    def reference_label(self):
        return naming.label(self)

    def emit_module(self, ctx):
        # the class exists even when no layout draws the button, for
        # Shortcut and Open Menu
        menu = ctx.name("class")
        ctx.module(f"""
            class {menu}(bpy.types.Menu):
                bl_idname = {menu!r}
                bl_label = {ctx.input("label")}

                def draw(self, context):
                    {ctx.flow("content", layout="self.layout")}
        """)

    def emit(self, ctx):
        menu = ctx.name("class")
        args = [repr(menu), f"text={ctx.input('label')}", icon_argument(ctx)]
        ctx.code(f"""
            {ctx.layout}.menu({", ".join(a for a in args if a)})
            {ctx.flow("next")}
        """)
