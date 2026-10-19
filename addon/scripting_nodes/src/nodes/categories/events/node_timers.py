"""Timers (bpy.app.timers): run a flow later or repeatedly. The timers stop
when the add-on is disabled (helpers run_later / run_in_intervals)."""

import bpy

from ....sockets.spec import Boolean, Float, Flow, Integer
from ...base_node import ScriptingBaseNode

PERSISTENT = bpy.props.BoolProperty(
    name="Keep on File Load",
    description="Keep the timer running when another file is opened",
)


def _persistent(node):
    return ", persistent=True" if node.persistent else ""


class SNA_Node_RunWithDelay(ScriptingBaseNode, bpy.types.Node):
    """Run nodes after some seconds. The flow continues right away; the
    Delayed flow runs later, with Blender's context at that time."""

    bl_idname = "SNA_Node_RunWithDelay"
    bl_label = "Run with Delay"
    sn_inputs = [Flow(), Float("delay", "Seconds", default=1.0)]
    sn_outputs = [Flow("delayed", "Delayed"), Flow("next")]

    persistent: PERSISTENT

    def draw(self, context, layout):
        layout.prop(self, "persistent")

    def emit(self, ctx):
        name = ctx.var("delayed")
        ctx.code(f"""
            def {name}():
                {ctx.flow("delayed")}
            {ctx.helper("run_later")}({name}, {ctx.input("delay")}{_persistent(self)})
            {ctx.flow("next")}
        """)


class SNA_Node_RunInIntervals(ScriptingBaseNode, bpy.types.Node):
    """Run nodes every few seconds: a number of times, or until Keep Running
    is off (checked after each run) or the add-on is disabled."""

    bl_idname = "SNA_Node_RunInIntervals"
    bl_label = "Run in Intervals"
    sn_inputs = [
        Flow(),
        Float("interval", "Seconds", default=1.0),
        Integer("times", "Times", default=0),
        Boolean("keep_running", "Keep Running", default=True),
    ]
    sn_outputs = [
        Flow("repeat", "Repeat"),
        Integer("index", "Index"),
        Flow("next"),
    ]

    persistent: PERSISTENT

    def draw(self, context, layout):
        layout.prop(self, "persistent")

    def emit(self, ctx):
        name, index = ctx.var("repeat"), ctx.var("index")
        repeat = ctx.flow("repeat", outputs={"index": index})
        args = [name, ctx.input("interval")]
        times = self.socket("times")
        if times.is_linked or times.value:
            args.append(ctx.input("times"))
        ctx.code(f"""
            def {name}({index}):
                {repeat}
                return {ctx.input("keep_running")}
            {ctx.helper("run_in_intervals")}({", ".join(args)}{_persistent(self)})
            {ctx.flow("next")}
        """)
