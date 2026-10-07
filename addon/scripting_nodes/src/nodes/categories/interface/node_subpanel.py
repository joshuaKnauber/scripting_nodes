import bpy

from ....sockets.spec import Boolean, Interface
from ...base_node import ScriptingBaseNode


class SNA_Node_Subpanel(ScriptingBaseNode, bpy.types.Node):
    """A collapsible section inside a panel (layout.panel)."""

    bl_idname = "SNA_Node_Subpanel"
    bl_label = "Subpanel"
    sn_inputs = [Interface(), Boolean("default_closed", "Default Closed")]
    sn_outputs = [
        Interface("header", "Header"),
        Interface("content", "Panel"),
        Interface("next", "After"),
    ]

    def emit(self, ctx):
        # layout.panel() only needs a unique id to remember the open state,
        # no Panel class is registered for it
        panel_id = ctx.class_name("PT", "Subpanel")
        header = ctx.var("header")
        body = ctx.var("panel")
        ctx.code(f"""
            {header}, {body} = {ctx.layout}.panel({panel_id!r}, default_closed={ctx.input("default_closed")})
            {ctx.flow("header", layout=header)}
            if {body}:
                {ctx.flow("content", layout=body)}
            {ctx.flow("next")}
        """)
