import bpy

from ....sockets.spec import Boolean, Flow
from ...base_node import ScriptingBaseNode


class SNA_Node_IfElse(ScriptingBaseNode, bpy.types.Node):
    """Run one of two branches depending on a condition. In an interface
    flow it draws one of them."""

    bl_idname = "SNA_Node_IfElse"
    bl_label = "If/Else"

    def socket_specs(self):
        kind = self.connected_flow_kind(outputs=("then", "else", "next"))
        return [Flow(kind=kind), Boolean("condition", "Condition")], [
            Flow("then", "Then", kind=kind),
            Flow("else", "Else", kind=kind),
            Flow("next", "After", kind=kind),
        ]

    def emit(self, ctx):
        ctx.code(f"""
            if {ctx.input("condition")}:
                {ctx.flow("then")}
            else:
                {ctx.flow("else")}
            {ctx.flow("next")}
        """)
