import bpy

from ....sockets.spec import Interface, String
from ...base_node import ScriptingBaseNode


class SNA_Node_Label(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Label"
    bl_label = "Label"
    sn_inputs = [Interface(), String("text", "Label")]
    sn_outputs = [Interface("next")]

    def emit(self, ctx):
        ctx.code(f"""
            {ctx.layout}.label(text={ctx.input("text")})
            {ctx.flow("next")}
        """)
