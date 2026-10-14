import bpy

from .....sockets.spec import Boolean, Interface
from ....base_node import ScriptingBaseNode


class SNA_Node_LayoutState(ScriptingBaseNode, bpy.types.Node):
    """Enable, deactivate or highlight the following elements of the layout."""

    bl_idname = "SNA_Node_LayoutState"
    bl_label = "Set Layout State"
    sn_inputs = [
        Interface(),
        Boolean("enabled", "Enabled", default=True),
        Boolean("active", "Active", default=True),
        Boolean("alert", "Alert", default=False),
    ]
    sn_outputs = [Interface("next")]

    operator_context: bpy.props.EnumProperty(
        name="Buttons Run",
        description="How buttons after it start their operator",
        items=[
            ("UNCHANGED", "Unchanged", "As set before (buttons invoke their operator)"),
            ("INVOKE_DEFAULT", "Invoke", "Invoke: dialogs and popups show"),
            ("EXEC_DEFAULT", "Execute", "Run right away, without dialogs"),
        ],
    )

    def draw(self, context, layout):
        layout.prop(self, "operator_context", text="")

    def emit(self, ctx):
        layout = ctx.layout
        operator_context = ""
        if self.operator_context != "UNCHANGED":
            operator_context = f"{layout}.operator_context = {self.operator_context!r}"
        ctx.code(f"""
            {layout}.enabled = {ctx.input("enabled")}
            {layout}.active = {ctx.input("active")}
            {layout}.alert = {ctx.input("alert")}
            {ctx.join([operator_context])}
            {ctx.flow("next")}
        """)
