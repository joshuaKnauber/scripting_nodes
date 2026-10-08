"""The API nodes use to write code: `NodeContext`, passed to `node.emit(ctx)`.

    def emit(self, ctx):
        ctx.code(f'''
            if {ctx.input("condition")}:
                {ctx.flow("then")}
            {ctx.flow("next")}
        ''')

Templates look like the generated code. `ctx.flow(key)` and `ctx.join(...)`
return placeholder tokens; when the template is written, each token is
replaced by the code it stands for, indented to the column the token sits
in. Single-line values (expressions, names) go straight into the f-string,
anything multi-line goes through a placeholder.
"""

import itertools
import re
import textwrap
from dataclasses import dataclass, field
from typing import NamedTuple

from ..lib.code_format import parenthesize
from ..lib.sockets import from_socket
from ..sockets.conversions import get_conversion
from ..sockets.spec import MISSING
from . import naming


class NodeError(Exception):
    """Raise from emit() to show a message on the node (it emits no code)."""


class Line(NamedTuple):
    indent: int
    text: str
    owner: str | None  # id of the node that wrote it


@dataclass
class Scope:
    """What's available where code is being written."""

    parent: "Scope | None" = None
    layout: str | None = None
    # (node pointer, output key) -> expression, for values only valid here
    values: dict = field(default_factory=dict)
    # names defined by the enclosing function (self, context, ...)
    names: frozenset = frozenset()

    def lookup(self, key):
        scope = self
        while scope is not None:
            if key in scope.values:
                return scope.values[key]
            scope = scope.parent
        return None


_token_ids = itertools.count()
_TOKEN = re.compile(r"⟦sn:\d+⟧")


def _is_value_node(node):
    """Nodes without flow sockets that aren't roots produce plain values."""
    if getattr(node, "sn_root", False):
        return False
    for socket in list(node.inputs) + list(node.outputs):
        if getattr(socket, "socket_type", "DATA") != "DATA":
            return False
    return True


def _def_names(lines, column):
    """Parameter names of the closest `def` enclosing `column`."""
    for line in reversed(lines):
        if line.text and line.indent < column:
            if line.text.startswith(("def ", "async def ")):
                params = line.text[line.text.index("(") + 1 : line.text.rindex(")")]
                names = set()
                for param in params.split(","):
                    name = param.split("=")[0].split(":")[0].strip().lstrip("*")
                    if name:
                        names.add(name)
                return frozenset(names)
            if not line.text.startswith(("@", "#")):
                # statements between us and a def don't end the search,
                # only a less indented class/def boundary would
                continue
    return None


class NodeContext:
    """Passed to `emit()`. See the module docstring and the docs site."""

    def __init__(self, builder, node, scope: Scope, mode: str):
        self._builder = builder
        self.node = node
        self.scope = scope
        self._mode = mode  # "root", "statement" or "value"
        self._lines: list[Line] = []
        self._tokens = {}
        self._at_module = False
        self.outputs = {}

    # -- build info -------------------------------------------------------

    @property
    def dev(self) -> bool:
        """True for the live addon, False when exporting. Prefer helpers."""
        return self._builder.dev

    @property
    def layout(self) -> str:
        """Expression of the current UI layout (inside interface flows)."""
        return self.scope.layout or "self.layout"

    # -- values -------------------------------------------------------------

    def input(self, key, default=MISSING) -> str:
        """Expression for input `key`: the connected value, else `default` if
        given, else the socket's own value."""
        socket = self.node.socket(key)
        if socket is None:
            raise NodeError(f"Node has no input '{key}'")
        if socket.is_linked:
            value = self._value_of(socket)
            if value is not None:
                return value
        if default is not MISSING:
            return default
        return socket.literal()

    def inputs(self, key) -> list[str]:
        """Expressions of all sockets of the dynamic input group `key`."""
        values = []
        for socket in self.node.dynamic_sockets(key):
            value = self._value_of(socket) if socket.is_linked else None
            values.append(value if value is not None else socket.literal())
        return values

    def is_linked(self, key) -> bool:
        socket = self.node.socket(key) or self.node.socket(key, output=True)
        return bool(socket and socket.is_linked)

    def output(self, key, expression: str):
        """Set data output `key`. From a flow node, the value is available to
        everything after it in the same flow."""
        if self._mode == "value":
            self.outputs[key] = expression
        else:
            self.scope.values[(self.node.as_pointer(), key)] = expression

    def resolve(self, prop):
        """The node a reference property points to, or None."""
        return self.node.resolve_reference(prop)

    def _value_of(self, socket):
        source = from_socket(socket)
        if source is None:
            return None
        producer = source.node
        expression = self.scope.lookup((producer.as_pointer(), source.identifier))
        if expression is None:
            if producer.bl_idname == "NodeGroupInput":
                raise NodeError(
                    f"'{source.name}' of the Group Input is only available in "
                    "the function's flow"
                )
            if _is_value_node(producer):
                expression = self._builder.evaluate(
                    producer, source.identifier, self.scope
                )
            else:
                raise NodeError(
                    f"'{source.name}' of '{producer.name}' isn't available here "
                    "(it only exists inside that node's flow)"
                )
        converted = get_conversion(source.bl_idname, socket.bl_idname, expression)
        return parenthesize(converted)

    # -- code ---------------------------------------------------------------

    def code(self, text: str):
        """Write a template where this node's code goes (in the flow, or at
        module level for root nodes)."""
        if self._mode == "value":
            raise NodeError("Value nodes can't write statements, use ctx.output()")
        lines = self._expand(text)
        if self._mode == "root":
            self._builder.add_block(lines)
        else:
            self._lines += lines

    def module(self, text: str):
        """Write a template at module level (classes, functions). Flows in it
        don't see values of the flow this node is in."""
        self._at_module = True
        try:
            self._builder.add_block(self._expand(text))
        finally:
            self._at_module = False

    def flow(self, key, layout=None, outputs=None) -> str:
        """Placeholder for the code connected to flow output `key`.

        `layout`: layout expression for interface flows below it.
        `outputs`: {output key: expression} values that only exist in there
        (e.g. a loop's item)."""
        socket = self.node.socket(key, output=True)
        if socket is None:
            raise NodeError(f"Node has no output '{key}'")
        values = {(self.node.as_pointer(), k): v for k, v in (outputs or {}).items()}

        def resolve(column, preceding):
            names = _def_names(preceding, column)
            base = self._builder.module_scope if self._at_module else self.scope
            scope = Scope(
                parent=base,
                layout=layout if layout is not None else base.layout,
                values=values,
                names=names if names is not None else base.names,
            )
            return self._builder.compile_flow(socket, scope)

        return self._token(resolve)

    def join(self, items) -> str:
        """Placeholder for several code items (strings, may be multi-line and
        contain other placeholders). Empty items are skipped."""
        items = [item for item in items if item and item.strip()]

        def resolve(column, preceding):
            lines = []
            for item in items:
                lines += self._expand(item)
            return lines

        return self._token(resolve)

    def _token(self, resolve):
        token = f"⟦sn:{next(_token_ids)}⟧"
        self._tokens[token] = resolve
        return token

    def _expand(self, text: str) -> list[Line]:
        lines = textwrap.dedent(text.strip("\n")).split("\n")
        out: list[Line] = []
        for raw in lines:
            stripped = raw.strip()
            if not stripped:
                out.append(Line(0, "", self.node.id))
                continue
            column = len(raw) - len(raw.lstrip())
            if _TOKEN.fullmatch(stripped):
                resolve = self._tokens.pop(stripped)
                for line in resolve(column, out):
                    if line.text:
                        out.append(Line(column + line.indent, line.text, line.owner))
                continue
            if _TOKEN.search(stripped):
                raise NodeError("ctx.flow() and ctx.join() must be on their own line")
            out.append(Line(column, raw.rstrip()[column:], self.node.id))
        return out

    # -- module level -------------------------------------------------------

    def imports(self, *lines):
        """Add import lines to the module (deduplicated)."""
        for line in lines:
            self._builder.imports.add(line.strip())

    def helper(self, name) -> str:
        """Name to call a shared helper (core/helpers.py) by."""
        return self._builder.use_helper(name)

    def symbol(self, owner, name) -> str:
        """`name` defined by another node or tree; imported if it lives in
        another tree's module."""
        return self._builder.import_symbol(owner, name)

    def on_register(self, line):
        self._builder.register.append(Line(0, line, self.node.id))

    def on_unregister(self, line):
        self._builder.unregister.append(Line(0, line, self.node.id))

    def var(self, name) -> str:
        """A unique local variable name, e.g. ctx.var("row") -> "row_1"."""
        return self._builder.unique_name(name)

    def class_name(self, kind, label="") -> str:
        return naming.class_name(self.node, kind, label)

    def idname(self, name) -> str:
        return naming.idname(self.node, name)

    def function_name(self, name) -> str:
        return naming.function_name(self.node, name)

    # -- used by the compiler -------------------------------------------------

    def lines(self) -> list[Line]:
        return self._lines


__all__ = ["NodeContext", "NodeError", "Scope", "Line"]
