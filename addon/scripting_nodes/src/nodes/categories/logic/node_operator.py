import bpy

from ....core import naming
from ....lib.code_format import literal_set
from ....lib.trees import node_by_id
from ....blend_data.rna import blend_data_spec
from ....sockets.spec import Boolean, Interface, List, Logic, String
from ..._property_list import PropertyListMixin
from ...base_node import ScriptingBaseNode


# Invoke behavior options
INVOKE_TYPE_ITEMS = [
    ("EXECUTE", "Execute", "Run execute() directly without invoke"),
    ("INVOKE", "Invoke", "Custom invoke behavior (use Invoke output)"),
    ("PROPS_DIALOG", "Properties Dialog", "Show properties dialog before executing"),
    ("PROPS_POPUP", "Properties Popup", "Show properties popup before executing"),
    ("CONFIRM", "Confirm", "Show confirmation dialog before executing"),
    ("FILE_BROWSER", "File Browser", "Pick a file or folder first (also for files dropped on Blender)"),
    ("MODAL", "Modal", "Keep running and react to every event (mouse, keys) until it ends"),
]  # fmt: skip

FILE_MODES = [
    ("OPEN_FILE", "Open File", "Pick one file", "FILE", 0),
    ("OPEN_FILES", "Open Files", "Pick one or more files", "DOCUMENTS", 1),
    ("SAVE_FILE", "Save File", "Type a name to save to", "FILE_TICK", 2),
    ("FOLDER", "Folder", "Pick a folder", "FILE_FOLDER", 3),
]

CURSORS = [
    (item.identifier, item.name, "", item.value)
    for item in bpy.types.Window.bl_rna.functions["cursor_modal_set"]
    .parameters["cursor"]
    .enum_items
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
        kind = node.invoke_type
        if kind in {"PROPS_DIALOG", "CONFIRM"}:
            col.prop(node, "dialog_title", placeholder="Operator's label")
            if kind == "CONFIRM":
                col.prop(node, "dialog_message", placeholder="Message")
            col.prop(node, "dialog_confirm_text", placeholder="OK")
            if kind == "PROPS_DIALOG":
                col.prop(node, "dialog_width")
        elif kind == "FILE_BROWSER":
            col.prop(node, "file_mode", text="")
            if node.file_mode != "FOLDER":
                col.prop(node, "file_filter", placeholder="*.png;*.jpg")
        elif kind == "MODAL":
            col.prop(node, "modal_cancel_keys")
            col.prop(node, "modal_timer")

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
            col.prop(node, "option_depends_on_cursor", toggle=True)
            if node.option_depends_on_cursor:
                col.prop(node, "cursor_pending", text="")

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
    option_depends_on_cursor: bpy.props.BoolProperty(
        name="Depends on Cursor",
        description=(
            "Started from a menu or the search, it waits for a click in the "
            "editor first (for operators that use the mouse position)"
        ),
    )
    cursor_pending: bpy.props.EnumProperty(
        name="Cursor", items=CURSORS, default="PICK_AREA",
        description="Mouse cursor while waiting for the click",
    )  # fmt: skip
    # dialogs
    dialog_title: bpy.props.StringProperty(name="Title")
    dialog_message: bpy.props.StringProperty(name="Message")
    dialog_confirm_text: bpy.props.StringProperty(name="Confirm Button")
    dialog_width: bpy.props.IntProperty(name="Width", default=300, min=100, max=1000)
    # file browser
    file_mode: bpy.props.EnumProperty(name="Pick", items=FILE_MODES)
    file_filter: bpy.props.StringProperty(
        name="Filter",
        description="Only show these files, e.g. *.png;*.jpg (empty: all files)",
    )
    # modal
    modal_cancel_keys: bpy.props.BoolProperty(
        name="Cancel with Esc / Right Click",
        description="End the operator (cancelled) when Esc or right mouse is pressed",
        default=True,
    )
    modal_timer: bpy.props.FloatProperty(
        name="Timer",
        description=(
            "Also run the Modal flow every this many seconds, without events "
            "(0: only for events)"
        ),
        min=0.0,
        soft_max=1.0,
    )

    @property
    def operator_idname(self):
        return self.sn_name("idname")

    def sn_names(self):
        label = naming.label(self)
        return [naming.Class("class", "OT", label), naming.Idname("idname", label)]

    def reference_label(self):
        label = self.socket("label")
        if label is not None and not label.is_linked and label.value:
            return label.value
        return self.label or self.name

    def socket_specs(self):
        inputs = [
            String("label", "Label", default="Operator"),
            Boolean("available", "Is Available", default=True),
        ]
        kind = self.invoke_type
        modal = kind == "MODAL"
        outputs = [
            Logic("execute", "Execute"),
            Logic("invoke", "Start" if modal else "Invoke", enabled=kind in {"INVOKE", "MODAL"}),
            Logic("modal", "Modal", enabled=modal),
            Logic("end", "End", enabled=modal),
            Interface("draw", "Draw", enabled=kind in {"PROPS_DIALOG", "PROPS_POPUP"}),
            blend_data_spec("event", "Event", "Event", enabled=kind in {"INVOKE", "MODAL"}),
        ]  # fmt: skip
        if kind == "FILE_BROWSER":
            if self.file_mode == "OPEN_FILES":
                outputs.append(List("paths", "File Paths"))
            else:
                label = "Folder" if self.file_mode == "FOLDER" else "File Path"
                outputs.append(String("path", label))
        return inputs, outputs + self.property_outputs()

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
            "DEPENDS_ON_CURSOR": self.option_depends_on_cursor,
        }
        options = {flag for flag, on in flags.items() if on}
        attributes = []
        if self.option_depends_on_cursor:
            attributes.append(f"bl_cursor_pending = {self.cursor_pending!r}")
        values = self.property_values()
        with_event = {**values, "event": "event"}
        kind = self.invoke_type
        methods = []
        execute_values = values
        if kind == "INVOKE":
            methods.append(f"""
                def invoke(self, context, event):
                    {ctx.flow("invoke", outputs=with_event)}
                    return self.execute(context)
            """)
        elif kind == "MODAL":
            methods += self._modal_methods(ctx, with_event)
        elif kind == "FILE_BROWSER":
            attributes += self._file_annotations()
            methods.append(FILE_INVOKE[self.file_mode])
            execute_values = {**values, **self._file_values(ctx)}
        elif kind in INVOKE_METHODS:
            methods.append(INVOKE_METHODS[kind].format(args=self._dialog_args()))
        if kind in {"PROPS_DIALOG", "PROPS_POPUP"} and ctx.is_linked("draw"):
            methods.append(f"""
                def draw(self, context):
                    {ctx.flow("draw", layout="self.layout", outputs=values)}
            """)

        if not ctx.is_default("available", True):
            methods.insert(
                0,
                f"""
                @classmethod
                def poll(cls, context):
                    return {ctx.input("available")}
            """,
            )
        # a modal operator only runs execute() when called with EXEC_DEFAULT
        if kind != "MODAL" or ctx.is_linked("execute"):
            methods.append(f"""
                def execute(self, context):
                    {ctx.flow("execute", outputs=execute_values)}
                    return {{"FINISHED"}}
            """)
        head = [
            f"bl_idname = {self.operator_idname!r}",
            f"bl_label = {ctx.input('label')}",
        ]
        if self.operator_description:
            head.append(f"bl_description = {self.operator_description!r}")
        head.append(f"bl_options = {literal_set(options)}")
        ctx.module(f"""
            class {ctx.name("class")}(bpy.types.Operator):
                {ctx.join(head)}
                {ctx.join(attributes)}
                {ctx.join(self.annotations(ctx))}

                {ctx.join(methods)}
        """)

    # -- dialogs ------------------------------------------------------------

    def _dialog_args(self):
        args = []
        if self.invoke_type == "PROPS_DIALOG" and self.dialog_width != 300:
            args.append(f"width={self.dialog_width}")
        if self.dialog_title:
            args.append(f"title={self.dialog_title!r}")
        if self.invoke_type == "CONFIRM" and self.dialog_message:
            args.append(f"message={self.dialog_message!r}")
        if self.dialog_confirm_text:
            args.append(f"confirm_text={self.dialog_confirm_text!r}")
        return "".join(", " + arg for arg in args)

    # -- file browser -------------------------------------------------------

    def _file_annotations(self):
        hidden = 'options={"HIDDEN", "SKIP_SAVE"}'
        mode = self.file_mode
        lines = []
        if mode in {"OPEN_FILE", "SAVE_FILE"}:
            lines.append(
                f'filepath: bpy.props.StringProperty(subtype="FILE_PATH", {hidden})'
            )
        else:
            lines.append(
                f'directory: bpy.props.StringProperty(subtype="DIR_PATH", {hidden})'
            )
        if mode == "OPEN_FILES":
            lines.append(
                "files: bpy.props.CollectionProperty("
                f"type=bpy.types.OperatorFileListElement, {hidden})"
            )
        if mode != "FOLDER" and self.file_filter.strip():
            lines.append(
                "filter_glob: bpy.props.StringProperty("
                f'default={self.file_filter.strip()!r}, options={{"HIDDEN"}})'
            )
        if mode == "SAVE_FILE":
            lines.append(
                'check_existing: bpy.props.BoolProperty(default=True, options={"HIDDEN"})'
            )
        return lines

    def _file_values(self, ctx):
        if self.file_mode == "OPEN_FILES":
            ctx.imports("import os")
            return {
                "paths": "[os.path.join(self.directory, file.name) for file in self.files]"
            }
        if self.file_mode == "FOLDER":
            return {"path": "self.directory"}
        return {"path": "self.filepath"}

    # -- modal --------------------------------------------------------------

    def _modal_methods(self, ctx, values):
        start, end = [], []
        if self.modal_timer > 0:
            start.append(
                "self._timer = context.window_manager.event_timer_add("
                f"{self.modal_timer!r}, window=context.window)"
            )
            end.append("context.window_manager.event_timer_remove(self._timer)")
        cancel = ""
        if self.modal_cancel_keys:
            cancel = """
                if event.type in {"ESC", "RIGHTMOUSE"} and event.value == "PRESS":
                    return {"CANCELLED"}
            """
        return [
            f"""
                def invoke(self, context, event):
                    {ctx.flow("invoke", outputs=values)}
                    {ctx.join(start)}
                    context.window_manager.modal_handler_add(self)
                    return {{"RUNNING_MODAL"}}

                def modal(self, context, event):
                    result = self._modal(context, event)
                    if result is None:
                        return {{"RUNNING_MODAL"}}
                    if not result & {{"RUNNING_MODAL", "PASS_THROUGH"}}:
                        self._end(context)
                    return result

                def _modal(self, context, event):
                    {ctx.join([cancel])}
                    {ctx.flow("modal", outputs=values)}

                def _end(self, context):
                    {ctx.join(end)}
                    {ctx.flow("end", outputs=self.property_values())}

                def cancel(self, context):
                    self._end(context)
            """
        ]


INVOKE_METHODS = {
    "PROPS_DIALOG": """
        def invoke(self, context, event):
            return context.window_manager.invoke_props_dialog(self{args})
    """,
    "PROPS_POPUP": """
        def invoke(self, context, event):
            return context.window_manager.invoke_props_popup(self, event)
    """,
    "CONFIRM": """
        def invoke(self, context, event):
            return context.window_manager.invoke_confirm(self, event{args})
    """,
}

# a file dropped on Blender (File Handler) is set before invoke: no browser
_BROWSE = """
            context.window_manager.fileselect_add(self)
            return {"RUNNING_MODAL"}
"""
FILE_INVOKE = {
    "OPEN_FILE": """
        def invoke(self, context, event):
            if self.filepath:
                return self.execute(context)"""
    + _BROWSE,
    "SAVE_FILE": """
        def invoke(self, context, event):"""
    + _BROWSE,
    "OPEN_FILES": """
        def invoke(self, context, event):
            if self.directory and self.files:
                return self.execute(context)"""
    + _BROWSE,
    "FOLDER": """
        def invoke(self, context, event):"""
    + _BROWSE,
}
