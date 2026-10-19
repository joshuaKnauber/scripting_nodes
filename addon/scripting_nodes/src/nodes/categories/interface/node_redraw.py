import bpy

from ....sockets.spec import Flow
from ...base_node import ScriptingBaseNode
from ..blender_data.node_context_checks import rna_items


class SNA_Node_Redraw(ScriptingBaseNode, bpy.types.Node):
    """Redraw editors, so panels show values changed by a timer, a handler
    or a property that Blender doesn't watch."""

    bl_idname = "SNA_Node_Redraw"
    bl_label = "Redraw"
    sn_inputs = [Flow()]
    sn_outputs = [Flow("next")]
    sn_header_props = ("area_type",)

    area_type: bpy.props.EnumProperty(
        name="Editors",
        items=[("ALL", "All Editors", "", "WINDOW", 1000)]
        + rna_items("Area", "type", skip=("EMPTY",)),
    )

    def emit(self, ctx):
        area_type = "" if self.area_type == "ALL" else repr(self.area_type)
        ctx.code(f"""
            {ctx.helper("redraw")}({area_type})
            {ctx.flow("next")}
        """)
