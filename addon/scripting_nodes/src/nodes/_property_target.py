"""Nodes that read, write or draw one property: Get/Set Property and the
UI fields (Checkbox, Number Field, ...).

The property is either
  - CUSTOM: a property node of this addon (reference field `prop`), or
  - BLENDER: a pasted Blender data path, e.g. `bpy.context.scene.frame_end`.

The node gets a "Data" input for the object that owns the property, unless
the owner is implicit (class properties of operators/preferences, or a
pasted path that already contains it).

    class SNA_Node_Checkbox(PropertyTargetMixin, ScriptingBaseNode, bpy.types.Node):
        sn_reference_properties = {"prop": BOOL_PROPERTY_NODES}

        def emit(self, ctx):
            data, name = self.property_target(ctx)
            ...
"""

import bpy

from ..blend_data.path_utils import format_name
from ..core.context import NodeError
from ..sockets.spec import BlendData

PREFERENCES_DATA = (
    'bpy.context.preferences.addons[__package__.rsplit(".", 1)[0]].preferences'
)


class PropertyTargetMixin:
    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ("CUSTOM", "Custom", "A property of this addon"),
            ("BLENDER", "Blender", "A Blender property (paste a data path)"),
        ],
        default="CUSTOM",
    )
    blend_data_path: bpy.props.StringProperty(name="Blend Data Path")
    blend_prop_name: bpy.props.StringProperty(name="Property Name")
    needs_data_input: bpy.props.BoolProperty(name="Needs Data Input")

    prop: bpy.props.StringProperty(name="Property")

    # -- resolution -------------------------------------------------------------

    def target_node(self):
        return self.resolve_reference("prop") if self.mode == "CUSTOM" else None

    def implicit_data(self):
        """Owner expression when it doesn't come from the Data input."""
        if self.mode == "BLENDER":
            if self.blend_prop_name and not self.needs_data_input:
                return self.blend_data_path or None
            return None
        target = self.target_node()
        register_on = getattr(target, "register_on", "")
        if register_on == "Operator":
            return "self"
        if register_on == "Preferences":
            return PREFERENCES_DATA
        return None

    def target_data_type(self, fallback="ScriptingDataSocket"):
        """Socket type of the targeted property's values."""
        target = self.target_node()
        return getattr(target, "data_type", fallback) if target else fallback

    def data_input_spec(self):
        """The Data input, hidden when the owner is implicit."""
        if self.mode == "BLENDER":
            hidden = bool(self.blend_prop_name) and not self.needs_data_input
        else:
            hidden = self.implicit_data() is not None
        return BlendData("data", "Data", hide=hidden)

    def property_target(self, ctx):
        """(owner expression, property name). Raises NodeError if incomplete."""
        if self.mode == "BLENDER":
            if not self.blend_prop_name:
                raise NodeError("Paste a property path")
            name = self.blend_prop_name
        else:
            target = self.target_node()
            if target is None:
                raise NodeError("Pick a property")
            name = target.prop_name
        data = self.implicit_data()
        if data is None:
            if not ctx.is_linked("data"):
                raise NodeError("Connect the data that owns the property")
            data = ctx.input("data")
        return data, name

    # -- blend data path operators (interface/ops/blend_data_path.py) -------

    def setup_from_path(self, path: str, prop_name: str, needs_input: bool):
        self.blend_data_path = path
        self.blend_prop_name = prop_name
        self.needs_data_input = needs_input
        self.label = format_name(prop_name) if prop_name else ""

    def clear_blend_data_path(self):
        self.blend_data_path = ""
        self.blend_prop_name = ""
        self.needs_data_input = False
        self.label = ""

    # -- UI -----------------------------------------------------------------

    def draw_target(self, layout):
        row = layout.row(align=True)
        if self.mode == "CUSTOM":
            self.draw_reference_prop(row, "prop")
            row.prop(self, "mode", icon="USER", icon_only=True, text="")
        else:
            if self.blend_prop_name:
                row.label(text=format_name(self.blend_prop_name))
                op = row.operator("sna.blend_data_clear_path", text="", icon="X")
            else:
                op = row.operator(
                    "sna.blend_data_paste_path", text="Paste Path", icon="PASTEDOWN"
                )
            op.node_name = self.name
            row.prop(self, "mode", icon="BLENDER", icon_only=True, text="")
