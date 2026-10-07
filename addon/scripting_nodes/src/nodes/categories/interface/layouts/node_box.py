import bpy

from .....sockets.spec import Interface
from ....base_node import ScriptingBaseNode


class SNA_Node_Box(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Box"
    bl_label = "Box"
    sn_inputs = [Interface()]
    sn_outputs = [Interface("content", "Box"), Interface("next", "After")]

    def emit(self, ctx):
        box = ctx.var("box")
        ctx.code(f"""
            {box} = {ctx.layout}.box()
            {ctx.flow("content", layout=box)}
            {ctx.flow("next")}
        """)
