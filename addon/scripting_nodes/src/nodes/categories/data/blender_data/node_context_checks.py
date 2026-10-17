"""Common questions about Blender's state: the mode, an object's type and
where an editor is open."""

import bpy

from .....blend_data.rna import blend_data_spec
from .....sockets.spec import Boolean, String
from ....base_node import ScriptingBaseNode


def rna_items(struct, prop, skip=()):
    """Enum items of a Blender property, numbered like Blender does (stable
    when Blender adds items)."""
    return [
        (item.identifier, item.name, item.description, item.icon, item.value)
        for item in getattr(bpy.types, struct).bl_rna.properties[prop].enum_items
        if item.identifier not in skip
    ]


class SNA_Node_IsInMode(ScriptingBaseNode, bpy.types.Node):
    """Whether Blender is in a mode (Object Mode, Edit Mode of a mesh,
    Sculpt Mode, ...), and the current mode's name."""

    bl_idname = "SNA_Node_IsInMode"
    bl_label = "Is in Mode"
    sn_outputs = [Boolean("is_in_mode", "Is in Mode"), String("mode", "Current Mode")]
    sn_header_props = ("mode",)

    mode: bpy.props.EnumProperty(
        name="Mode", items=rna_items("Context", "mode"), default="OBJECT"
    )

    def emit(self, ctx):
        ctx.output("is_in_mode", f"{ctx.context}.mode == {self.mode!r}")
        ctx.output("mode", f"{ctx.context}.mode")


class SNA_Node_IsObjectType(ScriptingBaseNode, bpy.types.Node):
    """Whether an object is a mesh, a curve, a light, ... False for None."""

    bl_idname = "SNA_Node_IsObjectType"
    bl_label = "Is Object Type"
    sn_inputs = [blend_data_spec("object", "Object", "Object")]
    sn_outputs = [Boolean("is_type", "Is Type")]
    sn_header_props = ("object_type",)

    object_type: bpy.props.EnumProperty(
        name="Type", items=rna_items("Object", "type"), default="MESH"
    )

    def emit(self, ctx):
        obj = ctx.input("object", default="None")
        ctx.output("is_type", f"getattr({obj}, 'type', None) == {self.object_type!r}")


class SNA_Node_AreaByType(ScriptingBaseNode, bpy.types.Node):
    """The first editor of a type in the current window (e.g. a 3D
    Viewport) and its main region, for Temp Override. None if there's none."""

    bl_idname = "SNA_Node_AreaByType"
    bl_label = "Area by Type"
    sn_outputs = [
        blend_data_spec("area", "Area", "Area"),
        blend_data_spec("region", "Region", "Region"),
        Boolean("found", "Found"),
    ]
    sn_header_props = ("area_type",)

    area_type: bpy.props.EnumProperty(
        name="Editor",
        items=rna_items("Area", "type", skip=("EMPTY",)),
        default="VIEW_3D",
    )

    def emit(self, ctx):
        screen = f"{ctx.context}.screen"
        area = (
            f"next((a for a in ({screen}.areas if {screen} else ()) "
            f"if a.type == {self.area_type!r}), None)"
        )
        ctx.output("area", area)
        ctx.output(
            "region",
            f"next((r for r in getattr({area}, 'regions', ()) if r.type == 'WINDOW'), None)",
        )
        ctx.output("found", f"{area} is not None")
