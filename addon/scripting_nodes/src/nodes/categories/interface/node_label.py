import bpy

from ....sockets.spec import Icon, Interface, String
from ..._icon import icon_argument
from ...base_node import ScriptingBaseNode


class SNA_Node_Label(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Label"
    bl_label = "Label"
    sn_inputs = [Interface(), String("text", "Label"), Icon()]
    sn_outputs = [Interface("next")]

    def emit(self, ctx):
        args = [f"text={ctx.input('text')}", icon_argument(ctx)]
        ctx.code(f"""
            {ctx.layout}.label({", ".join(a for a in args if a)})
            {ctx.flow("next")}
        """)
