"""Script node - Python from a Text block or a file, as a module of the add-on.

The script is added unchanged as `scripts/<name>.py`: its imports, classes
and its own `register()` / `unregister()` are part of the add-on. If it has a
`run()` function, the node calls it; the signature declares the sockets (see
nodes/_script_run.py):

    def run(context, obj: Object, factor: float = 2.0) -> int:
"""

import os

import bpy

from ....core import naming
from ....core.context import NodeError
from ....lib.trees import node_by_id
from ....sockets.spec import Flow, Socket
from ... import _script_run
from ...base_node import ScriptingBaseNode

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
    """Create a script from a template"""

    bl_idname = "sna.new_script"
    bl_label = "New Script"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        node = getattr(context, "node", None)
        if node is None:
            return {"CANCELLED"}
        text = bpy.data.texts.new("script.py")
        text.write(TEMPLATE)
        node.text_block = text
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


class SNA_Node_Script(ScriptingBaseNode, bpy.types.Node):
    """Add a Python script to the add-on and call its run() function."""

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

    def script_run(self):
        """`run()` of the script (nodes/_script_run.Run) or None."""
        try:
            return _script_run.read(self.script_source())
        except _script_run.ScriptError as exc:
            raise NodeError(f"Script: {exc}")

    # -- sockets ----------------------------------------------------------------

    def socket_specs(self):
        try:
            run = self.script_run()
        except NodeError:
            return self._current_specs()  # keep the links while it's broken
        if run is None:
            return [], []
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

    def emit_module(self, ctx):
        """The script as a module of the add-on, wherever the node is."""
        source = self.script_source()
        self.script_run()  # a syntax error shows on the node
        ctx.script("module", "alias", source)

    def emit(self, ctx):
        run = self.script_run()
        names = ctx.scope.names
        implicit = {
            "context": "context" if "context" in names else "bpy.context",
            "layout": ctx.layout,
            "self": "self" if "self" in names else "None",
            "event": "event" if "event" in names else "None",
        }
        args = [
            f"{name}={implicit[name] if name in implicit else ctx.input(name)}"
            for name in run.params
        ]
        call = f"{ctx.name('alias')}.run({', '.join(args)})"
        if run.outputs:
            results = [ctx.var(naming.snake(s.label, "result")) for s in run.outputs]
            for spec, result in zip(run.outputs, results):
                ctx.output(spec.key, result)
            call = f"{', '.join(results)} = {call}"
        ctx.code(f"""
            {call}
            {ctx.flow("next")}
        """)

    # -- UI -------------------------------------------------------------------

    def draw_label(self):
        source = self.source_name()
        return naming.snake(source[1]).replace("_", " ").title() if source else "Script"

    def draw(self, context, layout):
        layout.prop(self, "source_type", expand=True)
        if self.source_type == "EXTERNAL":
            layout.prop(self, "filepath", text="")
            return
        row = layout.row(align=True)
        row.template_ID(self, "text_block", new="sna.new_script", open="text.open")
        if self.text_block is not None:
            row.operator("sna.edit_script", text="", icon="TEXT").node_id = self.id
