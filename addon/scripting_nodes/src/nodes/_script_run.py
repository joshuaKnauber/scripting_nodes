"""The `run()` function of a script and the sockets its signature declares.

    def run(context, obj: Object, factor: float = 2.0) -> int:

gives the inputs Obj (Blend Data) and Factor (Float, 2.0) and an Integer
output. `context`, `layout`, `self` and `event` aren't inputs, the node passes
what the flow has; taking `layout` makes it an interface node. Several return
values are outputs named after the returned variables:

    def run(context) -> tuple[int, str]:
        ...
        return count, name
"""

import ast
from dataclasses import dataclass

import bpy

from ..sockets.spec import (
    BlendData,
    Boolean,
    Color,
    Data,
    Float,
    Integer,
    List,
    String,
    Vector,
)

IMPLICIT = ("self", "context", "layout", "event")

_TYPES = {"bool": Boolean, "int": Integer, "float": Float, "str": String}
_LISTS = {"list", "List", "tuple", "Tuple", "set", "Sequence", "Iterable"}


class ScriptError(Exception):
    """The script doesn't parse."""


@dataclass
class Run:
    params: list  # parameter names, in order
    inputs: list  # socket specs
    outputs: list  # socket specs, keys "output_0", "output_1", ...
    draws: bool  # takes `layout`


_cache: dict[str, Run | None] = {}


def read(source: str) -> Run | None:
    """`run()` of `source`, None if there is none. Raises ScriptError."""
    if source not in _cache:
        if len(_cache) > 64:
            _cache.clear()
        _cache[source] = _read(source)
    return _cache[source]


def _read(source):
    try:
        module = ast.parse(source)
    except SyntaxError as exc:
        raise ScriptError(f"Line {exc.lineno}: {exc.msg}") from None
    function = next(
        (
            item
            for item in module.body
            if isinstance(item, ast.FunctionDef) and item.name == "run"
        ),
        None,
    )
    if function is None:
        return None

    args = function.args
    positional = args.posonlyargs + args.args
    defaults = [None] * (len(positional) - len(args.defaults)) + args.defaults
    params = list(zip(positional, defaults)) + list(
        zip(args.kwonlyargs, args.kw_defaults)
    )
    inputs = [
        _socket(arg.annotation, arg.arg, _label(arg.arg), default)
        for arg, default in params
        if arg.arg not in IMPLICIT
    ]
    outputs = [
        _socket(annotation, f"output_{i}", label)
        for i, (label, annotation) in enumerate(_returns(function))
    ]
    names = [arg.arg for arg, _ in params]
    return Run(names, inputs, outputs, "layout" in names)


def _returns(function):
    """[(label, annotation)] of the values `function` returns."""
    annotation = function.returns
    values = [
        node.value
        for node in _own_nodes(function)
        if isinstance(node, ast.Return) and node.value is not None
    ]
    last = values[-1] if values else None
    if isinstance(annotation, ast.Constant) and annotation.value is None:
        return []
    if _type_name(annotation) in {"tuple", "Tuple"} and isinstance(
        annotation.slice, ast.Tuple
    ):
        types = annotation.slice.elts
    elif annotation is not None:
        types = [annotation]
    elif isinstance(last, ast.Tuple):
        types = [None] * len(last.elts)
    else:
        types = [None] if last is not None else []

    returned = last.elts if isinstance(last, ast.Tuple) else [last]
    if len(returned) != len(types):
        returned = [None] * len(types)
    labels = [_returned_label(node) for node in returned]
    if len(types) == 1:
        return [(labels[0] or "Result", types[0])]
    return [
        (label or f"Result {i + 1}", type_)
        for i, (label, type_) in enumerate(zip(labels, types))
    ]


def _own_nodes(function):
    """Nodes of `function`'s body, without those of nested functions."""
    stack = list(function.body)
    while stack:
        node = stack.pop()
        yield node
        if not isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Lambda)):
            stack.extend(ast.iter_child_nodes(node))


def _returned_label(node):
    if isinstance(node, ast.Name):
        return _label(node.id)
    if isinstance(node, ast.Attribute):
        return _label(node.attr)
    return ""


def _label(name):
    return name.replace("_", " ").strip().title()


def _type_name(annotation):
    """`bpy.types.Object` -> `Object`, `list[int]` -> `list`."""
    if isinstance(annotation, ast.Subscript):
        annotation = annotation.value
    if isinstance(annotation, ast.Attribute):
        return annotation.attr
    if isinstance(annotation, ast.Name):
        return annotation.id
    return ""


def _socket(annotation, key, label, default=None):
    """Socket spec for a value with `annotation` (an AST node or None)."""
    name = _type_name(annotation)
    try:
        value = ast.literal_eval(default) if default is not None else None
    except ValueError:
        value = None  # not a literal: no default on the socket

    if name in _TYPES:
        spec = _TYPES[name](key, label)
    elif name == "Vector":
        size = len(value) if isinstance(value, tuple) and 2 <= len(value) <= 4 else 3
        spec = Vector(key, label, dimension=size)
        value = value + (0.0,) * (4 - size) if isinstance(value, tuple) else None
    elif name == "Color":
        spec = Color(key, label)
        value = value + (1.0,) if isinstance(value, tuple) else None
    elif name in _LISTS:
        return List(key, label)
    elif name and hasattr(bpy.types, name):
        return BlendData(key, label)
    else:
        return Data(key, label)
    if value is not None:
        spec.default = value  # a value of the wrong type is skipped on creation
    return spec
