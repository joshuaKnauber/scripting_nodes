import bpy

from .....sockets.spec import Boolean, Interface
from ....base_node import ScriptingBaseNode
from ._sublayout import sublayout


class SNA_Node_LayoutState(ScriptingBaseNode, bpy.types.Node):
    """Enable, deactivate or highlight the elements after it. They're drawn
    in a layout of their own, so elements before it and after a Reset Layout
    aren't changed."""

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
        layout, create = sublayout(ctx)
        settings = [
            f"{layout}.{key} = {ctx.input(key)}"
            for key, default in (("enabled", True), ("active", True), ("alert", False))
            if not ctx.is_default(key, default)
        ]
        if self.operator_context != "UNCHANGED":
            settings.append(f"{layout}.operator_context = {self.operator_context!r}")
        ctx.code(f"""
            {create}
            {ctx.join(settings)}
            {ctx.flow("next", layout=layout, horizontal=ctx.horizontal)}
        """)
