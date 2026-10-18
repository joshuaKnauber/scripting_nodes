"""Converting between 3D locations and pixels of the 3D Viewport
(bpy_extras.view3d_utils), for the region and view the code runs in: a
Viewport Draw flow, or an operator started in the 3D Viewport."""

import bpy

from ....sockets.spec import Boolean, Vector
from ...base_node import ScriptingBaseNode


def _view(ctx):
    ctx.imports("from bpy_extras import view3d_utils")
    return f"{ctx.context}.region, {ctx.context}.region_data"


class SNA_Node_LocationToScreen(ScriptingBaseNode, bpy.types.Node):
    """Where a 3D location is on the screen, in pixels of the 3D Viewport:
    to draw text next to an object. Visible is off when it's behind the
    view."""

    bl_idname = "SNA_Node_LocationToScreen"
    bl_label = "Location to Screen"
    sn_inputs = [Vector("location", "Location", default=(0.0, 0.0, 0.0))]
    sn_outputs = [
        Vector("position", "Position", dimension=2),
        Boolean("visible", "Visible"),
    ]

    def emit(self, ctx):
        call = f"view3d_utils.location_3d_to_region_2d({_view(ctx)}, {ctx.input('location')})"
        ctx.output("position", f"({call} or (0.0, 0.0))")
        ctx.output("visible", f"{call} is not None")


class SNA_Node_ScreenToLocation(ScriptingBaseNode, bpy.types.Node):
    """The 3D location under a point of the 3D Viewport (in pixels, e.g. the
    mouse), at the depth of Depth. Ray Origin and Direction go from the
    view through that point, to cast rays into the scene."""

    bl_idname = "SNA_Node_ScreenToLocation"
    bl_label = "Screen to Location"
    sn_inputs = [
        Vector("position", "Position", default=(0.0, 0.0), dimension=2),
        Vector("depth", "Depth", default=(0.0, 0.0, 0.0)),
    ]
    sn_outputs = [
        Vector("location", "Location"),
        Vector("origin", "Ray Origin"),
        Vector("direction", "Ray Direction"),
    ]

    def emit(self, ctx):
        view, position = _view(ctx), ctx.input("position")
        ctx.output(
            "location",
            f"view3d_utils.region_2d_to_location_3d({view}, {position}, {ctx.input('depth')})",
        )
        ctx.output("origin", f"view3d_utils.region_2d_to_origin_3d({view}, {position})")
        ctx.output(
            "direction", f"view3d_utils.region_2d_to_vector_3d({view}, {position})"
        )
