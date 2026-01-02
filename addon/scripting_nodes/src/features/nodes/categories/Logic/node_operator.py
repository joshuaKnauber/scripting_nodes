from .....lib.utils.code.format import indent
from .....lib.utils.node_tree.scripting_node_trees import node_by_id
from ...base_node import ScriptingBaseNode
import bpy


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


class SNA_Node_Operator(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Operator"
    bl_label = "Operator"
    sn_options = {"ROOT_NODE"}

    # -- Properties --

    def update_props(self, context):
        self._generate()

    def _find_output(self, name):
        """Find an output socket by name (handles duplicates correctly)."""
        for socket in self.outputs:
            if socket.name == name:
                return socket
        return None

    def update_sockets(self, context):
        # Safety check: ensure node is fully initialized (Execute socket must exist)
        if self._find_output("Execute") is None:
            return

        # Ensure Invoke socket exists (for nodes created before this update)
        invoke_socket = self._find_output("Invoke")
        if invoke_socket is None:
            invoke_socket = self.add_output("ScriptingLogicSocket", "Invoke")
            invoke_socket.enabled = False
            # Move it after Execute
            self.outputs.move(len(self.outputs) - 1, 1)

        # Ensure Draw socket exists
        draw_socket = self._find_output("Draw")
        if draw_socket is None:
            draw_socket = self.add_output("ScriptingInterfaceSocket", "Draw")
            draw_socket.enabled = False
            # Move it after Invoke
            self.outputs.move(len(self.outputs) - 1, 2)

        # Update socket visibility based on invoke type
        invoke_socket.enabled = self.invoke_type == "INVOKE"
        # Draw is available for dialog/popup invoke types
        draw_socket.enabled = self.invoke_type in ("PROPS_DIALOG", "PROPS_POPUP")

        self._generate()

    operator_description: bpy.props.StringProperty(
        name="Description",
        description="Tooltip text shown when hovering over the operator",
        default="",
        update=update_props,
    )

    invoke_type: bpy.props.EnumProperty(
        items=INVOKE_TYPE_ITEMS,
        name="Invoke Type",
        description="How the operator is invoked when called",
        default="EXECUTE",
        update=update_sockets,
    )

    # Operator bl_options
    option_register: bpy.props.BoolProperty(
        name="Register",
        description="Display in the operator search popup and support the operator repeat last menu",
        default=True,
        update=update_props,
    )

    option_undo: bpy.props.BoolProperty(
        name="Undo",
        description="Push an undo step after the operator is executed",
        default=True,
        update=update_props,
    )

    option_undo_grouped: bpy.props.BoolProperty(
        name="Undo Grouped",
        description="Push a single undo step for repeated instances of this operator",
        default=False,
        update=update_props,
    )

    option_blocking: bpy.props.BoolProperty(
        name="Blocking",
        description="Block any other operators from running while this one is active",
        default=False,
        update=update_props,
    )

    option_internal: bpy.props.BoolProperty(
        name="Internal",
        description="Hide from operator search and do not show in info logs",
        default=False,
        update=update_props,
    )

    option_preset: bpy.props.BoolProperty(
        name="Preset",
        description="Enable operator preset menu (properties must be defined)",
        default=False,
        update=update_props,
    )

    def on_create(self):
        # Inputs
        self.add_input("ScriptingStringSocket", "Label").value = "Operator"
        self.add_input("ScriptingBooleanSocket", "Is Available").value = True

        # Outputs - execution hooks (using logic sockets)
        self.add_output("ScriptingLogicSocket", "Execute")
        invoke_out = self.add_output("ScriptingLogicSocket", "Invoke")
        invoke_out.enabled = False
        draw_out = self.add_output("ScriptingInterfaceSocket", "Draw")
        draw_out.enabled = False

    def draw(self, context, layout):
        # Settings and run buttons
        row = layout.row(align=True)
        settings_op = row.operator(
            "sna.operator_node_settings", text="Settings", icon="PREFERENCES"
        )
        settings_op.node_id = self.id

        # Play button to run the operator
        operator_idname = f"sna.operator_{self.id.lower()}"
        row.operator(operator_idname, text="", icon="PLAY")

    def generate(self):
        # Safety check: ensure inputs exist before generating
        if "Label" not in self.inputs or "Is Available" not in self.inputs:
            return

        # Build bl_options set
        options = []
        if self.option_register:
            options.append("'REGISTER'")
        if self.option_undo:
            options.append("'UNDO'")
        if self.option_undo_grouped:
            options.append("'UNDO_GROUPED'")
        if self.option_blocking:
            options.append("'BLOCKING'")
        if self.option_internal:
            options.append("'INTERNAL'")
        if self.option_preset:
            options.append("'PRESET'")
        options_str = "{" + ", ".join(options) + "}" if options else "set()"

        # Generate operator idname
        operator_idname = f"sna.operator_{self.id.lower()}"

        # Build class attributes list
        class_attrs = [
            f'bl_idname = "{operator_idname}"',
            f"bl_label = {self.inputs['Label'].eval()}",
        ]

        # Add description if provided
        if self.operator_description:
            class_attrs.append(f'bl_description = "{self.operator_description}"')

        # Add options
        class_attrs.append(f"bl_options = {options_str}")

        # Format class attributes
        attrs_code = "\n    ".join(class_attrs)

        # Build poll method
        poll_code = self.inputs["Is Available"].eval("True")
        poll_method = f"""
    @classmethod
    def poll(cls, context):
        return {poll_code}
"""

        # Build execute method
        execute_code = self.outputs["Execute"].eval("pass")
        execute_method = f"""
    def execute(self, context):
        {indent(execute_code, 2)}
        return {{"FINISHED"}}
"""

        # Build invoke method based on invoke_type
        invoke_method = ""
        if self.invoke_type == "INVOKE" and "Invoke" in self.outputs:
            invoke_code = self.outputs["Invoke"].eval("pass")
            invoke_method = f"""
    def invoke(self, context, event):
        {indent(invoke_code, 2)}
        return self.execute(context)
"""
        elif self.invoke_type == "PROPS_DIALOG":
            invoke_method = """
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
"""
        elif self.invoke_type == "PROPS_POPUP":
            invoke_method = """
    def invoke(self, context, event):
        return context.window_manager.invoke_props_popup(self, event)
"""
        elif self.invoke_type == "CONFIRM":
            invoke_method = """
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
"""

        # Build draw method if using dialog/popup invoke types
        draw_method = ""
        draw_socket = self._find_output("Draw")
        if self.invoke_type in ("PROPS_DIALOG", "PROPS_POPUP") and draw_socket:
            draw_socket.layout = f"layout_{self.id}"
            draw_code = draw_socket.eval("pass")
            draw_method = f"""
    def draw(self, context):
        layout_{self.id} = self.layout
        {indent(draw_code, 2)}
"""

        self.code = f"""
import bpy

class SNA_OT_Operator_{self.id}(bpy.types.Operator):
    {attrs_code}
{poll_method}{invoke_method}{draw_method}{execute_method}
"""
