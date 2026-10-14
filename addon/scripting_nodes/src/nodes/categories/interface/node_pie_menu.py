import bpy

from ....core import naming
from ....sockets.spec import Interface, String
from ...base_node import ScriptingBaseNode

# the order Blender fills a pie's slots in
DIRECTIONS = [
    ("left", "Left"),
    ("right", "Right"),
    ("bottom", "Bottom"),
    ("top", "Top"),
    ("top_left", "Top Left"),
    ("top_right", "Top Right"),
    ("bottom_left", "Bottom Left"),
    ("bottom_right", "Bottom Right"),
]


class SNA_Node_PieMenu(ScriptingBaseNode, bpy.types.Node):
    """A pie menu, opened around the mouse by a Shortcut or Open Menu. Each
    direction is one slot: connect a button, or a layout with several."""

    bl_idname = "SNA_Node_PieMenu"
    bl_label = "Pie Menu"
    sn_root = True
    sn_inputs = [String("label", "Label", default="Pie Menu")]
    sn_outputs = [Interface(key, label) for key, label in DIRECTIONS]

    def sn_names(self):
        return [naming.Class("class", "MT", naming.label(self))]

    def reference_label(self):
        return naming.label(self)

    def emit(self, ctx):
        menu = ctx.name("class")
        pie = ctx.var("pie")
        slots = []
        for key, _ in DIRECTIONS:
            if ctx.is_linked(key):
                column = ctx.var("column")
                slots.append(f"""
                    {column} = {pie}.column()
                    {ctx.flow(key, layout=column)}
                """)
            else:
                slots.append(f"{pie}.separator()")  # keeps the slot empty
        # trailing empty slots aren't needed
        while slots and slots[-1] == f"{pie}.separator()":
            slots.pop()
        ctx.module(f"""
            class {menu}(bpy.types.Menu):
                bl_idname = {menu!r}
                bl_label = {ctx.input("label")}

                def draw(self, context):
                    {pie} = self.layout.menu_pie()
                    {ctx.join(slots)}
        """)
