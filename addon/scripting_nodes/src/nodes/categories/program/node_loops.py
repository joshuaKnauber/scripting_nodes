import bpy

from ....sockets.spec import Flow, Integer
from ...base_node import ScriptingBaseNode


class SNA_Node_Repeat(ScriptingBaseNode, bpy.types.Node):
    """Run nodes a number of times. Index counts from 0."""

    bl_idname = "SNA_Node_Repeat"
    bl_label = "Repeat"
    sn_inputs = [Flow(), Integer("times", "Times", default=3)]
    sn_outputs = [Flow("loop", "Loop"), Flow("next", "Done"), Integer("index", "Index")]

    def emit(self, ctx):
        index = ctx.var("index")
        loop = ctx.flow("loop", outputs={"index": index})
        ctx.code(f"""
            for {index} in range({ctx.input("times")}):
                {loop}
            {ctx.flow("next")}
        """)


class SNA_Node_LoopControl(ScriptingBaseNode, bpy.types.Node):
    """In a loop (Repeat, For Each): stop it, or skip to the next item."""

    bl_idname = "SNA_Node_LoopControl"
    bl_label = "Break / Continue"
    sn_inputs = [Flow()]
    sn_header_props = ("action",)

    action: bpy.props.EnumProperty(
        name="Action",
        items=[
            ("break", "Stop Loop", "Leave the loop, continue after it (Done)"),
            ("continue", "Next Item", "Skip the rest of this run, go to the next item"),
        ],
    )

    def draw_label(self):
        return "Stop Loop" if self.action == "break" else "Next Item"

    def emit(self, ctx):
        ctx.code(self.action)
