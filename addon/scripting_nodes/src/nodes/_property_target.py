"""Nodes that read, write or draw one property: Get/Set Property and the
UI fields (Checkbox, Number Field, ...).

The property is either
  - CUSTOM: a property of this add-on (picked by id, settings/properties.py)
  - BLENDER: a pasted Blender data path, e.g. `bpy.context.scene.frame_end`

The node has a Data input for the data that owns the property. It is
optional when there's an obvious default (`context.scene` for Scene
properties, `self` for an operator's own properties) and hidden when the
owner can't be anything else.

    class SNA_Node_Checkbox(PropertyTargetMixin, ScriptingBaseNode, bpy.types.Node):
        sn_property_references = {"prop": "BOOLEAN"}

        def emit(self, ctx):
            data, name = self.property_target(ctx)
"""

import bpy

from ..blend_data.path_utils import format_name, is_data_path, is_identifier
from ..core import properties
from ..core.context import NodeError
from ..sockets.spec import BlendData


class PropertyTargetMixin:
    sn_property_references = {"prop": "ALL"}

    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ("CUSTOM", "Custom", "A property of this add-on"),
            ("BLENDER", "Blender", "A Blender property (paste a data path)"),
        ],
        default="CUSTOM",
    )
    blend_data_path: bpy.props.StringProperty(name="Blend Data Path")
    blend_prop_name: bpy.props.StringProperty(name="Property Name")
    needs_data_input: bpy.props.BoolProperty(name="Needs Data Input")

    # -- resolution -------------------------------------------------------------

    def target(self):
        """The picked property (core/properties.Found) or None."""
        if self.mode != "CUSTOM":
            return None
        return properties.find(getattr(self, "prop_id", ""))

    def target_prop(self):
        found = self.target()
        return found.prop if found else None

    def target_data_type(self, fallback="ScriptingDataSocket"):
        """Socket type of the targeted property's values."""
        prop = self.target_prop()
        return properties.socket_type(prop) if prop else fallback

    def data_input_spec(self):
        """The Data input, hidden when the owner is fixed."""
        if self.mode == "BLENDER":
            hidden = bool(self.blend_prop_name) and not self.needs_data_input
            return BlendData("data", "Data", hide=hidden)
        found = self.target()
        if found is None:
            return BlendData("data", "Data")
        if found.kind == "NODE":
            return BlendData("data", "Data", hide=True)
        if found.kind == "GROUP":
            return BlendData("data", found.owner.name)
        return BlendData("data", found.prop.attach_to)

    def property_target(self, ctx):
        """(expression of the data holding it, attribute name). Raises
        NodeError if incomplete."""
        if self.mode == "BLENDER":
            return self._blender_target(ctx)
        found = self.target()
        if found is None:
            raise NodeError("Pick a property")
        if ctx.is_linked("data") and found.kind != "NODE":
            owner = ctx.input("data")
        else:
            owner = properties.owner_expression(found, ctx.context)
            if owner is None:
                raise NodeError(
                    f"Connect the {self.data_input_spec().label} it belongs to"
                )
        return properties.holder(found, owner), properties.python_name(found)

    def _blender_target(self, ctx):
        if not self.blend_prop_name:
            raise NodeError("Paste a property path")
        # pasted text ends up in the generated code
        if not is_identifier(self.blend_prop_name):
            raise NodeError(f"Invalid property name: {self.blend_prop_name}")
        if self.blend_data_path and not is_data_path(self.blend_data_path):
            raise NodeError(f"Invalid data path: {self.blend_data_path}")
        if self.blend_data_path and not self.needs_data_input:
            return self.blend_data_path, self.blend_prop_name
        if not ctx.is_linked("data"):
            raise NodeError("Connect the data that owns the property")
        return ctx.input("data"), self.blend_prop_name

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
            category = self.sn_property_references["prop"]
            row.prop_search(
                self,
                "prop",
                bpy.context.scene.sna,
                properties.picker_attr(category),
                text="",
            )
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
