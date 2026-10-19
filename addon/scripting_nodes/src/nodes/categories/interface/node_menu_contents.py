import bpy

from ....core.context import NodeError
from ....core.references import Reference
from ....sockets.spec import Interface
from ...base_node import ScriptingBaseNode
from .node_add_to import class_name, classes


def _search_menus(self, context, edit_text):
    return [display for display, _ in classes(bpy.types.Menu)]


class SNA_Node_MenuContents(ScriptingBaseNode, bpy.types.Node):
    """Draw the entries of a menu right here instead of a button opening it:
    one of this add-on's menus or one of Blender's."""

    bl_idname = "SNA_Node_MenuContents"
    bl_label = "Menu Contents"
    bl_width_default = 200
    sn_inputs = [Interface()]
    sn_outputs = [Interface("next")]

    source: bpy.props.EnumProperty(
        name="Menu",
        items=[
            ("CUSTOM", "This Add-on", "A Menu node of this add-on", "NODETREE", 0),
            ("BLENDER", "Blender", "One of Blender's menus", "BLENDER", 1),
        ],
    )
    menu: Reference(("SNA_Node_Menu",), name="Menu", description="A Menu node")
    blender_menu: bpy.props.StringProperty(
        name="Blender Menu", description="One of Blender's menus", search=_search_menus
    )

    def draw(self, context, layout):
        row = layout.row(align=True)
        if self.source == "CUSTOM":
            self.draw_reference(row, "menu")
        else:
            row.prop(self, "blender_menu", text="")
        row.prop(self, "source", icon_only=True, text="")

    def emit(self, ctx):
        if self.source == "CUSTOM":
            target = ctx.resolve("menu")
            if target is None:
                raise NodeError("Pick a menu")
            name = target.sn_name("class")
        else:
            name = class_name(self.blender_menu)
            menu = getattr(bpy.types, name, None) if name.isidentifier() else None
            if not (isinstance(menu, type) and issubclass(menu, bpy.types.Menu)):
                raise NodeError("Pick one of Blender's menus")
        ctx.code(f"""
            {ctx.layout}.menu_contents({name!r})
            {ctx.flow("next")}
        """)
