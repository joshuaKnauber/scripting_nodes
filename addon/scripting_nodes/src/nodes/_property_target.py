"""Nodes that read, write or draw one property: Get/Set Property and the
UI fields (Checkbox, Number Field, ...).

The property is either
  - CUSTOM: a property node of this addon (reference field `prop`), with a
    "Data" input for the object that owns it unless the owner is implicit
    (class properties of operators/preferences), or
  - BLENDER: a Blender data path ending at the property, e.g. Scene › Render
    › FPS (nodes/_blend_path.py). The owner is the path without its last
    segment.

    class SNA_Node_Checkbox(PropertyTargetMixin, ScriptingBaseNode, bpy.types.Node):
        sn_reference_properties = {"prop": BOOL_PROPERTY_NODES}
        blender_prop_types = {"BOOLEAN"}

        def emit(self, ctx):
            data, name = self.property_target(ctx)
            ...
"""

import bpy

from ..blend_data import rna
from ..core.context import NodeError
from ..sockets.spec import BlendData, Socket
from ._blend_path import BlendPathMixin

PREFERENCES_DATA = (
    'bpy.context.preferences.addons[__package__.rsplit(".", 1)[0]].preferences'
)


class PropertyTargetMixin(BlendPathMixin):
    # RNA property types the Blender path search offers (None: all)
    blender_prop_types = None

    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ("CUSTOM", "Custom", "A property of this addon"),
            ("BLENDER", "Blender", "A Blender property (search or paste a data path)"),
        ],
        default="CUSTOM",
    )
    prop: bpy.props.StringProperty(name="Property")

    # -- resolution -------------------------------------------------------------

    def target_node(self):
        return self.resolve_reference("prop") if self.mode == "CUSTOM" else None

    def implicit_data(self):
        """Owner expression of a custom property when it doesn't come from
        the Data input."""
        target = self.target_node()
        register_on = getattr(target, "register_on", "")
        if register_on == "Operator":
            return "self"
        if register_on == "Preferences":
            return PREFERENCES_DATA
        return None

    def path_accepts(self, step):
        if step.is_subscript or step.prop is None:
            return False
        return (
            self.blender_prop_types is None or step.prop.type in self.blender_prop_types
        )

    def target_input_specs(self):
        """Inputs for the owner: the Data input, plus the path's keys."""
        if self.mode == "BLENDER":
            return self.path_input_specs()
        return [BlendData("data", "Data", hide=self.implicit_data() is not None)]

    def target_value_spec(self, key, label):
        """Socket for values of the targeted property."""
        if self.mode == "BLENDER":
            return rna.value_spec(self.path_final(), key, label)
        target = self.target_node()
        idname = getattr(target, "data_type", "ScriptingDataSocket")
        spec = Socket(idname, key, label)
        size = getattr(target, "prop_size", None)
        if size and idname == "ScriptingVectorSocket" and 2 <= size <= 4:
            spec.attrs["dimension"] = str(size)
        elif idname == "ScriptingColorSocket":
            spec.attrs["use_alpha"] = size == 4
        return spec

    def property_target(self, ctx):
        """(owner expression, property name). Raises NodeError if incomplete."""
        if self.mode == "BLENDER":
            parts = self.path_parts()
            if parts is None:
                raise NodeError(f"Invalid data path: {self.path}")
            if not parts:
                raise NodeError("Search or paste a property")
            if parts[-1] == rna.SUBSCRIPT:
                raise NodeError("The path has to end at a property")
            return self.path_expression(ctx, len(parts) - 1), parts[-1]

        target = self.target_node()
        if target is None:
            raise NodeError("Pick a property")
        data = self.implicit_data()
        if data is None:
            if not ctx.is_linked("data"):
                raise NodeError("Connect the data that owns the property")
            data = ctx.input("data")
        return data, target.prop_name

    # -- UI -----------------------------------------------------------------

    def draw_target(self, layout):
        if self.mode == "CUSTOM":
            row = layout.row(align=True)
            self.draw_reference_prop(row, "prop")
            row.prop(self, "mode", icon="USER", icon_only=True, text="")
        else:
            self.draw_path(
                layout,
                header=lambda row: row.prop(
                    self, "mode", icon="BLENDER", icon_only=True, text=""
                ),
            )
