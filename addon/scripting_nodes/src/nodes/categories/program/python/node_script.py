"""Script node - Python from a Text block or a file.

The node uses the script in one of three ways (`function_name`):

- Run the Code: the code is put where the node is in the flow, like a Python
  Statement of several lines.
- Add to Add-on: the script is added unchanged as a module,
  `scripts/<name>.py`; its classes are registered, its `register()` /
  `unregister()` called. The default for scripts defining those.
- A function: added like that, and the node calls the function; its
  signature declares the sockets (see nodes/_script_run.py):

    def run(context, obj: Object, factor: float = 2.0) -> int:
"""

import os
import zlib

import bpy

from .....core import naming
from .....core.context import NodeError
from .....lib.trees import node_by_id
from .....sockets.spec import Flow, Socket
from .node_python_code import MODULES
from .... import _script_run
from ....base_node import ScriptingBaseNode

TEMPLATE = '''import bpy


def run(context, name: str = "World") -> str:
    """Parameters are the node's inputs, return values its outputs.
    `context` (also `layout`, `self`, `event`) is passed in."""
    message = f"Hello {name} from {context.scene.name}!"
    return message


# Optional: called when the add-on is enabled / disabled
# def register():
#     ...
#
# def unregister():
#     ...
'''


class SNA_OT_NewScript(bpy.types.Operator):
    """Create a script from a template (into the picked text if it's empty)"""

    bl_idname = "sna.new_script"
    bl_label = "New Script"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_id: bpy.props.StringProperty(options={"HIDDEN"})

    def execute(self, context):
        node = node_by_id(self.node_id)
        if node is None:
            return {"CANCELLED"}
        text = node.text_block
        if text is None:
            text = bpy.data.texts.new("script.py")
        text.clear()
        text.write(TEMPLATE)
        node.text_block = text
        node.function_name = "run"
        return {"FINISHED"}


class SNA_OT_EditScript(bpy.types.Operator):
    """Show the script in a Text Editor (a new window if there is none)"""

    bl_idname = "sna.edit_script"
    bl_label = "Edit Script"
    bl_options = {"REGISTER", "INTERNAL"}

    node_id: bpy.props.StringProperty(options={"HIDDEN"})

    def execute(self, context):
        node = node_by_id(self.node_id)
        if node is None or node.text_block is None:
            return {"CANCELLED"}
        editors = [a for a in context.screen.areas if a.type == "TEXT_EDITOR"]
        if not editors:
            bpy.ops.wm.window_new()
            editors = context.window_manager.windows[-1].screen.areas[:1]
            editors[0].type = "TEXT_EDITOR"
        editors[0].spaces.active.text = node.text_block
        return {"FINISHED"}


# `function_name` besides function names; "" picks one from the script
RUN_CODE = ":code"
ADD_TO_ADDON = ":addon"
_items = []  # Blender needs the items of dynamic enums kept alive


def _value(name):
    """A stable enum value per function name: the picked function stays
    picked when functions are added or moved."""
    return zlib.crc32(name.encode()) & 0x7FFFFFFF or 2


def _function_items(self, context):
    items = [
        (RUN_CODE, "Run the Code", "Put the code where the node is in the flow", 0),
        (
            ADD_TO_ADDON,
            "Add to Add-on",
            "Make the script part of the add-on: its classes are registered, its "
            "register() and unregister() called",
            1,
        ),
    ]
    for name in self.script_functions():
        items.append((name, f"{name}()", f"Call {name}() of the script", _value(name)))
    _items[:] = items
    return _items


def _get_function(self):
    try:
        use = self.script_use()
    except NodeError:
        return 0
    fixed = {RUN_CODE: 0, ADD_TO_ADDON: 1}
    return fixed[use] if use in fixed else _value(use)


def _set_function(self, value):
    names = {0: RUN_CODE, 1: ADD_TO_ADDON}
    names.update({_value(name): name for name in self.script_functions()})
    self.function_name = names.get(value, "")


class SNA_Node_Script(ScriptingBaseNode, bpy.types.Node):
    """Python from a text block or a file: its code where the node is, or
    one of its functions called with the node's inputs."""

    bl_idname = "SNA_Node_Script"
    bl_label = "Script"
    bl_width_default = 200

    source_type: bpy.props.EnumProperty(
        items=[
            ("INTERNAL", "Text", "Use a text block from the blend file"),
            ("EXTERNAL", "File", "Use an external Python file"),
        ],
        name="Source",
        description="Where to load the script from",
        default="INTERNAL",
    )
    text_block: bpy.props.PointerProperty(
        type=bpy.types.Text, name="Text", description="Text block with the script"
    )
    filepath: bpy.props.StringProperty(
        name="File", description="Path to a Python file", subtype="FILE_PATH"
    )
    function_name: bpy.props.StringProperty(
        name="Function", description="Function of the script the node calls"
    )
    function: bpy.props.EnumProperty(
        name="Function",
        description="Call a function of the script, its parameters and return "
        "values become sockets",
        items=_function_items,
        get=_get_function,
        set=_set_function,
    )
    data_only: bpy.props.BoolProperty(
        name="Data Only",
        description="No flow sockets: call the function where its results are "
        "used (once per used result)",
    )

    # -- source ---------------------------------------------------------------

    def source_name(self):
        """(owner, base name) of the script's module, or None. Nodes using
        the same text or file share the module."""
        if self.source_type == "INTERNAL":
            if self.text_block is None:
                return None
            name = self.text_block.name
            return "text:" + name, os.path.splitext(name)[0]
        if not self.filepath:
            return None
        path = os.path.normpath(bpy.path.abspath(self.filepath))
        return "file:" + path, os.path.splitext(os.path.basename(path))[0]

    def source_fingerprint(self):
        """Changes whenever the script source changes (watched in nodes/_text_source.py)."""
        if self.source_type == "INTERNAL":
            return hash(self.text_block.as_string()) if self.text_block else None
        path = bpy.path.abspath(self.filepath) if self.filepath else ""
        try:
            stat = os.stat(path)
            return (path, stat.st_mtime_ns, stat.st_size)
        except OSError:
            return (path, None)

    def script_source(self):
        if self.source_type == "INTERNAL":
            if self.text_block is None:
                raise NodeError("Pick a text block")
            return self.text_block.as_string()
        if not self.filepath:
            raise NodeError("Pick a Python file")
        path = bpy.path.abspath(self.filepath)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except OSError as exc:
            raise NodeError(f"Can't read {path}: {exc.strerror or exc}")

    def script(self):
        """What the script defines (nodes/_script_run.Script)."""
        try:
            return _script_run.read(self.script_source())
        except _script_run.ScriptError as exc:
            raise NodeError(f"Script: {exc}")

    def script_functions(self):
        """Names of the script's functions, [] if it can't be read."""
        if self.source_name() is None:
            return []
        try:
            return list(self.script().functions)
        except NodeError:
            return []

    def script_use(self):
        """RUN_CODE, ADD_TO_ADDON or the name of the function the node calls.
        Without a choice: add-on code (classes, register()) is added to the
        add-on, other code runs."""
        script = self.script()
        if self.function_name in (RUN_CODE, ADD_TO_ADDON):
            return self.function_name
        if self.function_name in script.functions:
            return self.function_name
        return ADD_TO_ADDON if script.is_module else RUN_CODE

    def picked_function(self):
        """(name, Run) of the function the node calls, or None."""
        use = self.script_use()
        if use in (RUN_CODE, ADD_TO_ADDON):
            return None
        return use, self.script().functions[use]

    def is_data_only(self, run):
        return self.data_only and bool(run.outputs) and not run.draws

    # -- sockets ----------------------------------------------------------------

    def socket_specs(self):
        try:
            script = self.script()
            picked = self.picked_function()
        except NodeError:
            return self._current_specs()  # keep the links while it's broken
        if picked is None:
            if self.script_use() == ADD_TO_ADDON:
                return [], []
            kind = "INTERFACE" if script.uses_layout else "PROGRAM"
            return [Flow(kind=kind)], [Flow("next", kind=kind)]
        run = picked[1]
        if self.is_data_only(run):
            return list(run.inputs), list(run.outputs)
        kind = "INTERFACE" if run.draws else "PROGRAM"
        return (
            [Flow(kind=kind), *run.inputs],
            [Flow("next", kind=kind), *run.outputs],
        )

    def _current_specs(self):
        def spec(socket):
            result = Socket(socket.bl_idname, socket.identifier, socket.name)
            if hasattr(socket, "kind"):
                result.kind = socket.kind
            for attr in ("dimension", "use_alpha"):
                if hasattr(socket, attr):
                    result.attrs[attr] = getattr(socket, attr)
            return result

        return [spec(s) for s in self.inputs], [spec(s) for s in self.outputs]

    # -- code -------------------------------------------------------------------

    def sn_names(self):
        source = self.source_name()
        if source is None:
            return []
        owner, base = source
        return [
            naming.Script("module", base, owner),
            naming.Symbol("alias", naming.snake(base, "script"), owner=owner),
        ]

    def is_inline(self):
        return self.script_use() == RUN_CODE

    def emit_module(self, ctx):
        """The script as a module of the add-on (wherever the node is), unless
        its code goes where the node is."""
        source = self.script_source()
        if not self.is_inline():
            ctx.script("module", "alias", source)

    def emit(self, ctx):
        picked = self.picked_function()
        if picked is None:
            if self.script_use() == ADD_TO_ADDON:
                return
            ctx.code(f"""
                {ctx.join(self._inline_code(ctx))}
                {ctx.flow("next")}
            """)
            return
        name, run = picked
        names = ctx.scope.names
        implicit = {
            "context": ctx.context,
            "layout": ctx.layout,
            "self": "self" if "self" in names else "None",
            "event": "event" if "event" in names else "None",
        }
        args = [
            f"{param}={implicit[param] if param in implicit else ctx.input(param)}"
            for param in run.params
        ]
        call = f"{ctx.name('alias')}.{name}({', '.join(args)})"
        if self.is_data_only(run):
            if len(run.outputs) == 1:
                ctx.output(run.outputs[0].key, call)
            else:
                for i, spec in enumerate(run.outputs):
                    ctx.output(spec.key, f"{call}[{i}]")
            return
        if run.outputs:
            results = [ctx.var(naming.snake(s.label, "result")) for s in run.outputs]
            for spec, result in zip(run.outputs, results):
                ctx.output(spec.key, result)
            call = f"{', '.join(results)} = {call}"
        ctx.code(f"""
            {call}
            {ctx.flow("next")}
        """)

    def _inline_code(self, ctx):
        """The script as it is, after the names it uses from the flow."""
        source = self.script_source()
        script = self.script()
        lines = []
        if ctx.context != "context":
            lines.append(f"context = {ctx.context}")
        if script.uses_layout and ctx.layout != "layout":
            lines.append(f"layout = {ctx.layout}")
        for module in MODULES:
            if f"{module}." in source and module != "bpy":
                ctx.imports(f"import {module}")
        lines.append(source)
        return lines

    # -- UI -------------------------------------------------------------------

    def draw_label(self):
        source = self.source_name()
        if source is None:
            return "Script"
        return "Script: " + naming.snake(source[1]).replace("_", " ").title()

    def draw(self, context, layout):
        layout.prop(self, "source_type", expand=True)
        if self.source_type == "EXTERNAL":
            layout.prop(self, "filepath", text="")
        else:
            row = layout.row(align=True)
            row.prop(self, "text_block", text="")
            if self.text_block is None:
                row.operator("sna.new_script", text="", icon="ADD").node_id = self.id
            else:
                op = row.operator("sna.edit_script", text="", icon="TEXT")
                op.node_id = self.id
        if self.source_name() is None:
            return
        try:
            picked = self.picked_function()
        except NodeError:
            return  # shows on the node
        if self.text_block is not None and not self.text_block.as_string().strip():
            layout.label(text="The script is empty", icon="INFO")
            op = layout.operator("sna.new_script", text="Add Template", icon="FILE")
            op.node_id = self.id
            return
        layout.prop(self, "function", text="")
        if picked is not None:
            run = picked[1]
            if run.outputs and not run.draws:
                layout.prop(self, "data_only")
