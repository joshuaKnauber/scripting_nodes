"""Python Expression / Python Statement: a line of Python typed on the node.

Names the code uses that Python doesn't know become inputs:
`obj.location.z * factor` gets the inputs obj and factor. Common modules
(math, random, ...) are imported when used, `context` is Blender's context.
The inputs are put into the code, so the generated add-on contains the line
with the connected values in place of the names.
"""

import ast
import builtins

import bpy

from .....core.context import NodeError
from .....sockets.spec import Data, Flow
from ....base_node import ScriptingBaseNode

MODULES = (
    "bpy", "bmesh", "math", "mathutils", "random", "os", "re", "time",
    "datetime", "json", "pathlib",
)  # fmt: skip
IMPLICIT = ("context", "self", "layout", "event")
_BUILTINS = set(dir(builtins))
INPUT_PREFIX = "name_"


def parse(code, mode):
    """The syntax tree of `code`, None if it isn't valid Python."""
    try:
        return ast.parse(code, mode=mode)
    except SyntaxError:
        return None


def _bound_names(tree):
    """Names the code defines itself (assignments, loop and comprehension
    variables, lambda arguments, imports)."""
    bound = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            bound.add(node.id)
        elif isinstance(node, ast.arg):
            bound.add(node.arg)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            bound.update((a.asname or a.name).split(".")[0] for a in node.names)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            bound.add(node.name)
    return bound


def free_names(tree):
    """Names the code reads that aren't defined, built in, modules or
    Blender's context: the inputs. In order of appearance."""
    if tree is None:
        return []
    skip = _bound_names(tree) | _BUILTINS | set(MODULES) | set(IMPLICIT)
    found = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
        and isinstance(node.ctx, ast.Load)
        and node.id not in skip
    ]
    found.sort(key=lambda node: (node.lineno, node.col_offset))
    return list(dict.fromkeys(node.id for node in found))


class _Substitute(ast.NodeTransformer):
    def __init__(self, values):
        self.values = values

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and node.id in self.values:
            return self.values[node.id]
        return node


class PythonCodeNode(ScriptingBaseNode):
    """Base of Python Expression (mode "eval") and Python Statement ("exec")."""

    mode = "eval"
    bl_width_default = 240

    code: bpy.props.StringProperty(name="Code", description="A line of Python")

    def tree(self):
        return parse(self.code, self.mode)

    def input_specs(self):
        return [Data(INPUT_PREFIX + name, name) for name in free_names(self.tree())]

    def draw(self, context, layout):
        row = layout.row()
        row.alert = bool(self.code.strip()) and self.tree() is None
        row.prop(self, "code", text="")

    def python(self, ctx):
        """The code with the inputs and implicit names put in, and its
        imports added."""
        if not self.code.strip():
            raise NodeError("Type some Python")
        tree = self.tree()
        if tree is None:
            raise NodeError("Not valid Python")
        values = {}
        for name in free_names(tree):
            values[name] = ast.parse(ctx.input(INPUT_PREFIX + name), mode="eval").body
        used = {
            node.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
        } - _bound_names(tree)
        if "context" in used:
            values["context"] = ast.parse(ctx.context, mode="eval").body
        for name in ("self", "layout", "event"):
            if name in used and name not in ctx.scope.names:
                raise NodeError(f"'{name}' isn't available here")
        for module in MODULES:
            if module in used and module != "bpy":
                ctx.imports(f"import {module}")
        tree = ast.fix_missing_locations(_Substitute(values).visit(tree))
        return ast.unparse(tree)


class SNA_Node_PythonExpression(PythonCodeNode, bpy.types.Node):
    """A Python expression typed on the node, e.g. `round(value * 100)`.
    Names Python doesn't know become inputs."""

    bl_idname = "SNA_Node_PythonExpression"
    bl_label = "Python Expression"
    mode = "eval"

    def socket_specs(self):
        return self.input_specs(), [Data("result", "Result")]

    def emit(self, ctx):
        ctx.output("result", self.python(ctx))


class SNA_Node_PythonStatement(PythonCodeNode, bpy.types.Node):
    """Python statements typed on the node, e.g. `obj.hide_set(True)`.
    Separate several with `;`. Names Python doesn't know become inputs."""

    bl_idname = "SNA_Node_PythonStatement"
    bl_label = "Python Statement"
    mode = "exec"

    def socket_specs(self):
        return [Flow(), *self.input_specs()], [Flow("next")]

    def emit(self, ctx):
        ctx.code(f"""
            {ctx.join([self.python(ctx)])}
            {ctx.flow("next")}
        """)
