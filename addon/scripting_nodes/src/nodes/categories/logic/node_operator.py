import bpy

from ....core import naming
from ....lib.code_format import literal_set
from ....lib.trees import node_by_id
from ....sockets.spec import Boolean, Interface, Logic, String
from ..._property_list import PropertyListMixin
from ...base_node import ScriptingBaseNode


# Invoke behavior options
INVOKE_TYPE_ITEMS = [
    ("EXECUTE", "Execute", "Run execute() directly without invoke"),
    ("INVOKE", "Invoke", "Custom invoke behavior (use Invoke output)"),
    ("PROPS_DIALOG", "Properties Dialog", "Show properties dialog before executing"),
    ("PROPS_POPUP", "Properties Popup", "Show properties popup before executing"),
    ("CONFIRM", "Confirm", "Show confirmation dialog before executing"),
]


class SNA_OT_OperatorNodeSettings(bpy.types.Operator):
    bl_idname = "sna.operator_node_settings"
    bl_label = "Operator Settings"
    bl_description = "Configure operator settings"
    bl_options = {"REGISTER", "INTERNAL"}

    node_id: bpy.props.StringProperty()
    show_options: bpy.props.BoolProperty(default=False)

    def draw(self, context):
        layout = self.layout
        node = node_by_id(self.node_id)
        if not node:
            layout.label(text="Node not found")
            return

        # Description
        col = layout.column(align=True)
        col.label(text="Description")
        col.prop(node, "operator_description", text="")

        layout.separator()

        # Invoke type
        col = layout.column(align=True)
        col.label(text="Invoke Behavior")
        col.prop(node, "invoke_type", text="")

        layout.separator()

        # Options toggle section
        box = layout.box()
        row = box.row()
        row.prop(
            self,
            "show_options",
            text="Options",
            icon="TRIA_DOWN" if self.show_options else "TRIA_RIGHT",
            emboss=False,
        )

        if self.show_options:
            col = box.column(align=True)
            col.prop(node, "option_register", toggle=True)
            col.prop(node, "option_undo", toggle=True)
            col.prop(node, "option_undo_grouped", toggle=True)
            col.prop(node, "option_blocking", toggle=True)
            col.prop(node, "option_internal", toggle=True)
            col.prop(node, "option_preset", toggle=True)

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=220)


class SNA_Node_Operator(PropertyListMixin, ScriptingBaseNode, bpy.types.Node):
    """An operator (button action) of the addon. Its properties (sidebar)
    are its inputs: shown in dialogs, set by Run Operator / Button, and
    available as outputs in its flows."""

    bl_idname = "SNA_Node_Operator"
    bl_label = "Operator"
    sn_root = True

    operator_description: bpy.props.StringProperty(
        name="Description", description="Tooltip of the operator"
    )
    invoke_type: bpy.props.EnumProperty(
        items=INVOKE_TYPE_ITEMS,
        name="Invoke Type",
        description="What happens when the operator is started from the UI",
        default="EXECUTE",
    )
    option_register: bpy.props.BoolProperty(
        name="Register",
        description="Show in the operator search and support Adjust Last Operation",
        default=True,
    )
    option_undo: bpy.props.BoolProperty(
        name="Undo",
        description="Push an undo step after the operator ran",
        default=True,
    )
    option_undo_grouped: bpy.props.BoolProperty(
        name="Undo Grouped", description="One undo step for repeated runs"
    )
    option_blocking: bpy.props.BoolProperty(
        name="Blocking", description="Block other operators while running"
    )
    option_internal: bpy.props.BoolProperty(
        name="Internal", description="Hide from the operator search"
    )
    option_preset: bpy.props.BoolProperty(
        name="Preset", description="Show a preset menu for the properties"
    )

    @property
    def operator_idname(self):
        return self.sn_name("idname")

    def sn_names(self):
        label = naming.label(self)
        return [naming.Class("class", "OT", label), naming.Idname("idname", label)]

    def socket_specs(self):
        inputs = [
            String("label", "Label", default="Operator"),
            Boolean("available", "Is Available", default=True),
        ]
        outputs = [
            Logic("execute", "Execute"),
            Logic("invoke", "Invoke", enabled=self.invoke_type == "INVOKE"),
            Interface(
                "draw",
                "Draw",
                enabled=self.invoke_type in {"PROPS_DIALOG", "PROPS_POPUP"},
            ),
        ] + self.property_outputs()
        return inputs, outputs

    def draw(self, context, layout):
        row = layout.row(align=True)
        op = row.operator(
            "sna.operator_node_settings", text="Settings", icon="PREFERENCES"
        )
        op.node_id = self.id
        try:
            row.operator(self.operator_idname, text="", icon="PLAY")
        except (RuntimeError, AttributeError):
            pass
        self.draw_property_names(layout)

    def emit(self, ctx):
        flags = {
            "REGISTER": self.option_register,
            "UNDO": self.option_undo,
            "UNDO_GROUPED": self.option_undo_grouped,
            "BLOCKING": self.option_blocking,
            "INTERNAL": self.option_internal,
            "PRESET": self.option_preset,
        }
        options = {flag for flag, on in flags.items() if on}
        values = self.property_values()
        methods = [INVOKE_METHODS.get(self.invoke_type, "")]
        if self.invoke_type == "INVOKE":
            methods = [
                f"""
                def invoke(self, context, event):
                    {ctx.flow("invoke", outputs=values)}
                    return self.execute(context)
            """
            ]
        if self.invoke_type in {"PROPS_DIALOG", "PROPS_POPUP"} and ctx.is_linked(
            "draw"
        ):
            methods.append(f"""
                def draw(self, context):
                    {ctx.flow("draw", layout="self.layout", outputs=values)}
            """)

        ctx.module(f"""
            class {ctx.name("class")}(bpy.types.Operator):
                bl_idname = {self.operator_idname!r}
                bl_label = {ctx.input("label")}
                bl_description = {self.operator_description!r}
                bl_options = {literal_set(options)}
                {ctx.join(self.annotations(ctx))}

                @classmethod
                def poll(cls, context):
                    return {ctx.input("available")}

                {ctx.join(methods)}

                def execute(self, context):
                    {ctx.flow("execute", outputs=values)}
                    return {{"FINISHED"}}
        """)


INVOKE_METHODS = {
    "PROPS_DIALOG": """
        def invoke(self, context, event):
            return context.window_manager.invoke_props_dialog(self)
    """,
    "PROPS_POPUP": """
        def invoke(self, context, event):
            return context.window_manager.invoke_props_popup(self, event)
    """,
    "CONFIRM": """
        def invoke(self, context, event):
            return context.window_manager.invoke_confirm(self, event)
    """,
}
