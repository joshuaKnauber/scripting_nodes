"""Add to Menu / Panel / Header: draw into one of Blender's (or another
add-on's) menus, panels or headers with `<class>.append(draw)`."""

import bpy

from ....core import naming
from ....core.context import NodeError
from ....sockets.spec import Boolean, Interface
from ...base_node import ScriptingBaseNode
from .ops import add_to_picker

POSITIONS = [
    ("append", "End", "Draw after the existing contents"),
    ("prepend", "Start", "Draw before the existing contents"),
]


def classes(base):
    """(display, class name) of every registered subclass of `base` ("Object
    [VIEW3D_MT_object]"), sorted by label."""
    entries = []
    for name in dir(bpy.types):
        cls = getattr(bpy.types, name, None)
        if not isinstance(cls, type) or not issubclass(cls, base) or cls is base:
            continue
        if name.startswith("SNA_"):
            continue  # Scripting Nodes' own UI
        label = getattr(cls, "bl_label", "") or name
        entries.append((f"{label}  [{name}]", name))
    entries.sort(key=lambda e: e[0].lower())
    return entries


def class_name(value: str) -> str:
    """The class name of a search field value ("Object  [VIEW3D_MT_object]"
    or a typed name)."""
    value = value.strip()
    if value.endswith("]") and "  [" in value:
        value = value[value.rindex("  [") + 3 : -1]
    return value


class AddToNode(ScriptingBaseNode):
    """Base of the Add to nodes. Subclasses set `base` (bpy.types.Menu, ...)
    and `kind` (what the target is called)."""

    sn_root = True
    sn_inputs = [Boolean("visible", "Is Visible", default=True)]
    sn_outputs = [Interface("draw", "Interface")]
    base = None
    kind = ""

    position: bpy.props.EnumProperty(name="Position", items=POSITIONS)

    def target_class(self):
        name = class_name(self.target)
        cls = getattr(bpy.types, name, None) if name.isidentifier() else None
        if isinstance(cls, type) and issubclass(cls, self.base):
            return name
        return None

    def sn_names(self):
        name = self.target_class() or ""
        label = getattr(getattr(bpy.types, name, None), "bl_label", "") or name
        text = f"draw_{naming.snake(label, 'nothing')}_{self.kind}"
        return [naming.Symbol("function", text)]

    def draw(self, context, layout):
        if add_to_picker.is_active(self):
            row = layout.row()
            row.alert = True
            row.operator("sna.add_to_picker_cancel", icon="X")
            layout.label(text="Click a Pick button", icon="INFO")
            return
        row = layout.row(align=True)
        row.prop(self, "target", text="", icon="VIEWZOOM")
        row.operator(
            "sna.add_to_picker_start", text="", icon="EYEDROPPER"
        ).node_id = self.id
        layout.prop(self, "position", expand=True)

    def emit(self, ctx):
        name = self.target_class()
        if name is None:
            if self.target:
                raise NodeError(f"No {self.kind} '{class_name(self.target)}'")
            raise NodeError(f"Pick a {self.kind}")
        function = ctx.name("function")
        visible = self.socket("visible")
        check = ""
        if visible.is_linked or not visible.value:
            check = f"""
                if not {ctx.input("visible")}:
                    return
            """
        ctx.module(f"""
            def {function}(self, context):
                {ctx.join([check])}
                {ctx.flow("draw", layout="self.layout")}
        """)
        ctx.on_register(f"bpy.types.{name}.{self.position}({function})")
        ctx.on_unregister(f"bpy.types.{name}.remove({function})")


def _search(base):
    def search(self, context, edit_text):
        return [display for display, _ in classes(base)]

    return search


class SNA_Node_AddToMenu(AddToNode, bpy.types.Node):
    """Draw into one of Blender's menus, e.g. the 3D Viewport's Object menu
    or a right-click menu."""

    bl_idname = "SNA_Node_AddToMenu"
    bl_label = "Add to Menu"
    base = bpy.types.Menu
    kind = "menu"

    target: bpy.props.StringProperty(
        name="Menu",
        description="The menu to draw into (its class name with Python Tooltips)",
        search=_search(bpy.types.Menu),
    )


class SNA_Node_AddToPanel(AddToNode, bpy.types.Node):
    """Draw into one of Blender's panels, below its contents."""

    bl_idname = "SNA_Node_AddToPanel"
    bl_label = "Add to Panel"
    base = bpy.types.Panel
    kind = "panel"

    target: bpy.props.StringProperty(
        name="Panel",
        description="The panel to draw into",
        search=_search(bpy.types.Panel),
    )


class SNA_Node_AddToHeader(AddToNode, bpy.types.Node):
    """Draw into an editor's header, e.g. the 3D Viewport's header."""

    bl_idname = "SNA_Node_AddToHeader"
    bl_label = "Add to Header"
    base = bpy.types.Header
    kind = "header"

    target: bpy.props.StringProperty(
        name="Header",
        description="The header to draw into",
        search=_search(bpy.types.Header),
    )
