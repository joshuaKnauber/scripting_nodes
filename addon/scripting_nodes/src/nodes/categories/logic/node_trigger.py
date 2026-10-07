import bpy

from ....core import naming
from ....sockets.spec import Logic
from ...base_node import ScriptingBaseNode


class SNA_Node_Trigger(ScriptingBaseNode, bpy.types.Node):
    """Run a flow with a button on the node (for testing while building)."""

    bl_idname = "SNA_Node_Trigger"
    bl_label = "Trigger"
    sn_root = True
    sn_outputs = [Logic()]

    @property
    def operator_idname(self):
        return naming.idname(self, "trigger")

    def draw(self, context, layout):
        row = layout.row()
        row.scale_y = 1.5
        try:
            row.operator(self.operator_idname, text="Trigger")
        except (RuntimeError, AttributeError):
            row.label(text="Trigger (addon not loaded)", icon="ERROR")

    def emit(self, ctx):
        ctx.module(f"""
            class {ctx.class_name("OT", "Trigger")}(bpy.types.Operator):
                bl_idname = {self.operator_idname!r}
                bl_label = "Trigger"
                bl_options = {{"REGISTER", "UNDO"}}

                def execute(self, context):
                    {ctx.flow("flow")}
                    return {{"FINISHED"}}
        """)
