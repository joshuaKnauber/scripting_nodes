"""Inline Script: the code of a Text block or a file, put where the node is in
the flow, like a Python Statement of several lines. Names the code uses
without defining them become inputs, given their values before the code;
variables it assigns can be picked as outputs (the variable is the value)."""

import ast

import bpy

from .....core.context import NodeError
from .....core.scripts import ScriptSource
from .....lib.trees import node_by_id
from .....settings.scripts import draw_source
from .....sockets.spec import Data, Flow
from ....base_node import ScriptingBaseNode
from ._script_nodes import current_specs
from .node_python_code import INPUT_PREFIX, MODULES, free_names, parse

TEMPLATE = """# Runs where the node is in the flow. `context` is Blender's context
# (`layout` in a panel). Names the code uses without defining them become
# inputs of the node, variables it assigns can be added as outputs.
for obj in context.selected_objects:
    obj.location.z += 1
moved = len(context.selected_objects)
"""

OUTPUT_PREFIX = "var_"
_SCOPES = (
    ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda,
    ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp,
)  # fmt: skip


def assigned_names(tree):
    """Variables the code assigns outside functions, classes and
    comprehensions, in order."""
    if tree is None:
        return []
    found = []
    stack = list(reversed(tree.body))
    while stack:
        node = stack.pop()
        if isinstance(node, _SCOPES):
            continue
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            found.append(node.id)
        stack.extend(reversed(list(ast.iter_child_nodes(node))))
    return list(dict.fromkeys(found))


_items = []  # Blender needs the items of dynamic enums kept alive


def _output_items(self, context):
    node = node_by_id(self.node_id)
    names = (
        [n for n in node.assigned() if n not in node.outputs_picked()] if node else []
    )
    _items[:] = [(n, n, "") for n in names] or [("", "No Variables", "")]
    return _items


class SNA_OT_InlineScriptAddOutput(bpy.types.Operator):
    """Make a variable the code assigns an output"""

    bl_idname = "sna.inline_script_add_output"
    bl_label = "Add Output"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    bl_property = "variable"

    node_id: bpy.props.StringProperty(options={"HIDDEN"})
    variable: bpy.props.EnumProperty(name="Variable", items=_output_items)

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        node = node_by_id(self.node_id)
        if node is None or not self.variable:
            return {"CANCELLED"}
        node.output_names = ",".join([*node.outputs_picked(), self.variable])
        return {"FINISHED"}


class SNA_OT_InlineScriptRemoveOutput(bpy.types.Operator):
    """Remove the output"""

    bl_idname = "sna.inline_script_remove_output"
    bl_label = "Remove Output"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_id: bpy.props.StringProperty(options={"HIDDEN"})
    variable: bpy.props.StringProperty(options={"HIDDEN"})

    def execute(self, context):
        node = node_by_id(self.node_id)
        if node is None:
            return {"CANCELLED"}
        names = [n for n in node.outputs_picked() if n != self.variable]
        node.output_names = ",".join(names)
        return {"FINISHED"}


class SNA_Node_InlineScript(ScriptSource, ScriptingBaseNode, bpy.types.Node):
    """Python from a text block or a file, run where the node is in the flow:
    a few lines for an operator or a panel. Names it doesn't define become
    inputs, variables it assigns can be outputs."""

    bl_idname = "SNA_Node_InlineScript"
    bl_label = "Inline Script"
    bl_width_default = 200
    sn_template = TEMPLATE
    sn_template_name = "inline.py"

    source_type: bpy.props.EnumProperty(
        items=[
            ("INTERNAL", "Text", "Use a text block from the blend file"),
            ("EXTERNAL", "File", "Use an external Python file"),
        ],
        name="Source",
        description="Where to load the script from",
    )
    text_block: bpy.props.PointerProperty(
        type=bpy.types.Text, name="Text", description="Text block with the code"
    )
    filepath: bpy.props.StringProperty(
        name="File", description="Path to a Python file", subtype="FILE_PATH"
    )
    output_names: bpy.props.StringProperty(
        name="Outputs", description="Variables of the code that are outputs"
    )

    # -- the code -----------------------------------------------------------------

    def code_tree(self):
        try:
            return parse(self.script_source(), "exec")
        except NodeError:
            return None

    def input_names(self):
        return free_names(self.code_tree())

    def assigned(self):
        return assigned_names(self.code_tree())

    def outputs_picked(self):
        return [n for n in self.output_names.split(",") if n]

    # -- sockets ------------------------------------------------------------------

    def socket_specs(self):
        try:
            script = self.script()
        except NodeError:
            if self.source_name() is None:
                return [Flow()], [Flow("next")]
            return current_specs(self)  # keep the links while it's broken
        kind = "INTERFACE" if script.uses_layout else "PROGRAM"
        inputs = [Data(INPUT_PREFIX + name, name) for name in self.input_names()]
        outputs = [Data(OUTPUT_PREFIX + name, name) for name in self.outputs_picked()]
        return [Flow(kind=kind), *inputs], [Flow("next", kind=kind), *outputs]

    # -- code ---------------------------------------------------------------------

    def emit(self, ctx):
        source = self.script_source()
        script = self.script()
        tree = self.code_tree()
        used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        for name in sorted({"self", "event"} & used - set(ctx.scope.names)):
            raise NodeError(f"'{name}' isn't available here")
        assigned = self.assigned()
        for name in self.outputs_picked():
            if name not in assigned:
                raise NodeError(f"The code doesn't assign '{name}' anymore")
            ctx.output(OUTPUT_PREFIX + name, name)
        lines = []
        if ctx.context != "context":
            lines.append(f"context = {ctx.context}")
        if script.uses_layout and ctx.layout != "layout":
            lines.append(f"layout = {ctx.layout}")
        for name in self.input_names():
            value = ctx.input(INPUT_PREFIX + name)
            if value != name:
                lines.append(f"{name} = {value}")
        for module in MODULES:
            if f"{module}." in source and module != "bpy":
                ctx.imports(f"import {module}")
        lines.append(source)
        ctx.code(f"""
            {ctx.join(lines)}
            {ctx.flow("next")}
        """)

    # -- UI -----------------------------------------------------------------------

    def draw_label(self):
        if self.source_name() is None:
            return "Inline Script"
        return f"Inline Script: {self.source_label()}"

    def draw(self, context, layout):
        if not draw_source(layout, self):
            return
        col = layout.column(align=True)
        for name in self.outputs_picked():
            row = col.row(align=True)
            row.label(text=name, icon="FORWARD")
            op = row.operator(
                "sna.inline_script_remove_output", text="", icon="X", emboss=False
            )
            op.node_id, op.variable = self.id, name
        op = col.operator("sna.inline_script_add_output", text="Output", icon="ADD")
        op.node_id = self.id
