"""Nodes that read, write or draw one property: Get/Set Property and the
UI fields (Checkbox, Number Field, ...).

The property is either
  - CUSTOM: a property of this add-on (picked by id, settings/properties.py),
    with a Data input for the data that owns it. The input is optional when
    there's an obvious default (`context.scene` for Scene properties, `self`
    for an operator's own properties) and hidden when the owner can't be
    anything else, or
  - BLENDER: a Blender data path ending at the property, e.g. Scene › Render
    › FPS (nodes/_blend_path.py). The owner is the path without its last
    segment.

    class SNA_Node_Checkbox(PropertyTargetMixin, ScriptingBaseNode, bpy.types.Node):
        sn_property_references = {"prop": "BOOLEAN"}
        blender_prop_types = {"BOOLEAN"}

        def emit(self, ctx):
            data, name = self.property_target(ctx)
"""

import bpy

from ..blend_data import rna
from ..core import properties
from ..core.context import NodeError
from ..sockets.spec import BlendData, Socket
from ._blend_path import BlendPathMixin
from ._property_list import SELF

PREFERENCES = "SNA_Node_Preferences"


class PropertyTargetMixin(BlendPathMixin):
    sn_property_references = {"prop": "ALL"}
    # RNA property types the Blender path search offers (None: all)
    blender_prop_types = None

    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ("CUSTOM", "This Add-on", "A property of this add-on"),
            ("BLENDER", "Blender", "A Blender property (search or paste a data path)"),
        ],
        default="CUSTOM",
    )

    # -- resolution -------------------------------------------------------------

    def target(self):
        """The picked property (core/properties.Found) or None."""
        if self.mode != "CUSTOM":
            return None
        return properties.find(getattr(self, "prop_id", ""))

    def target_prop(self):
        found = self.target()
        return found.prop if found else None

    def path_accepts(self, step):
        if step.is_subscript or step.prop is None:
            return False
        return (
            self.blender_prop_types is None or step.prop.type in self.blender_prop_types
        )

    def _data_input_spec(self):
        found = self.target()
        if found is None:
            return BlendData("data", "Data")
        if found.kind == "NODE":
            return BlendData("data", "Data", hide=True)
        if found.kind == "GROUP":
            return BlendData("data", found.owner.name)
        return BlendData("data", found.prop.attach_to)

    def target_input_specs(self):
        """Inputs for the owner: the Data input, or the path's keys."""
        if self.mode == "BLENDER":
            return self.path_input_specs()
        return [self._data_input_spec()]

    def target_value_spec(self, key, label):
        """Socket for values of the targeted property."""
        if self.mode == "BLENDER":
            return rna.value_spec(self.path_final(), key, label)
        prop = self.target_prop()
        if prop is None:
            return Socket("ScriptingDataSocket", key, label)
        spec = Socket(properties.socket_type(prop), key, label)
        spec.attrs.update(properties.socket_attrs(prop))
        return spec

    def property_target(self, ctx):
        """(expression of the data holding it, attribute name). Raises
        NodeError if incomplete."""
        if self.mode == "BLENDER":
            parts = self.path_parts()
            if parts is None:
                raise NodeError(f"Invalid data path: {self.path}")
            if not parts:
                raise NodeError("Search or paste a property")
            if parts[-1] == rna.SUBSCRIPT:
                raise NodeError("The path has to end at a property")
            return self.path_expression(ctx, len(parts) - 1), parts[-1]

        found = self.target()
        if found is None:
            raise NodeError("Pick a property")
        if ctx.is_linked("data") and found.kind != "NODE":
            owner = ctx.input("data")
        else:
            owner = properties.owner_expression(found, ctx.context)
            if found.kind == "NODE":
                # in the operator's / preferences' own methods: `self`
                inside = ctx.scope.lookup((found.owner.as_pointer(), SELF))
                if inside is None and found.owner.bl_idname != PREFERENCES:
                    raise NodeError(
                        f"Only inside '{found.owner.name}': it's that "
                        "operator's property"
                    )
                owner = inside or owner
            if owner is None:
                raise NodeError(
                    f"Connect the {self._data_input_spec().label} it belongs to"
                )
        return properties.holder(found, owner), properties.python_name(found)

    def setup_hint(self):
        if self.mode == "BLENDER":
            return None if self.path else "Search or paste a property"
        if properties.is_missing(self, "prop"):
            return "The property it used was deleted"
        if self.target() is None:
            return "Pick a property"
        return super().setup_hint()

    # -- UI -----------------------------------------------------------------

    def draw_target(self, layout):
        if self.mode == "CUSTOM":
            row = properties.draw_reference(layout, self, "prop")
            row.prop(self, "mode", icon="NODETREE", icon_only=True, text="")
        else:
            self.draw_path(
                layout,
                header=lambda row: row.prop(
                    self, "mode", icon="BLENDER", icon_only=True, text=""
                ),
            )
