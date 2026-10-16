"""
Socket type conversion utilities.

This module provides automatic conversion between different data socket types.
When a socket of one type is connected to a socket of a different type,
the appropriate conversion wrapper is applied to the generated code.
"""

# Conversion functions for each target type
# Format: (from_type, to_type) -> conversion_template
# The template uses {value} as a placeholder for the source code. None marks
# types that can't be converted (ConversionError, shown on the node).

import ast

from ..lib.code_format import is_simple, parenthesize

CONVERSIONS = {
    # To String
    ("ScriptingBooleanSocket", "ScriptingStringSocket"): "str({value})",
    ("ScriptingFloatSocket", "ScriptingStringSocket"): "str({value})",
    ("ScriptingIntegerSocket", "ScriptingStringSocket"): "str({value})",
    ("ScriptingVectorSocket", "ScriptingStringSocket"): "str({value})",
    ("ScriptingColorSocket", "ScriptingStringSocket"): "str({value})",
    # Blender data as text is its name, not "<bpy_struct, Object(...)>"
    ("ScriptingDataSocket", "ScriptingStringSocket"): "{as_text}({value})",
    ("ScriptingBlendDataSocket", "ScriptingStringSocket"): "{as_text}({value})",
    # To Boolean
    ("ScriptingStringSocket", "ScriptingBooleanSocket"): "bool({value})",
    ("ScriptingFloatSocket", "ScriptingBooleanSocket"): "bool({value})",
    ("ScriptingIntegerSocket", "ScriptingBooleanSocket"): "bool({value})",
    ("ScriptingVectorSocket", "ScriptingBooleanSocket"): "bool({value})",
    ("ScriptingColorSocket", "ScriptingBooleanSocket"): "bool({value})",
    ("ScriptingDataSocket", "ScriptingBooleanSocket"): "bool({value})",
    ("ScriptingBlendDataSocket", "ScriptingBooleanSocket"): "bool({value})",
    # To Float
    (
        "ScriptingStringSocket",
        "ScriptingFloatSocket",
    ): "(float({value}) if str({value}).replace('.','',1).replace('-','',1).isdigit() else 0.0)",
    ("ScriptingBooleanSocket", "ScriptingFloatSocket"): "float({value})",
    # Python mixes ints and floats in arithmetic: no float() needed
    ("ScriptingIntegerSocket", "ScriptingFloatSocket"): "{value}",
    (
        "ScriptingVectorSocket",
        "ScriptingFloatSocket",
    ): "(float({value}[0]) if hasattr({value}, '__getitem__') else 0.0)",
    (
        "ScriptingColorSocket",
        "ScriptingFloatSocket",
    ): "(float({value}[0]) if hasattr({value}, '__getitem__') else 0.0)",
    (
        "ScriptingDataSocket",
        "ScriptingFloatSocket",
    ): "(float({value}) if isinstance({value}, (int, float)) else 0.0)",
    ("ScriptingBlendDataSocket", "ScriptingFloatSocket"): None,
    # To Integer
    (
        "ScriptingStringSocket",
        "ScriptingIntegerSocket",
    ): "(int(float({value})) if str({value}).replace('.','',1).replace('-','',1).isdigit() else 0)",
    ("ScriptingBooleanSocket", "ScriptingIntegerSocket"): "int({value})",
    ("ScriptingFloatSocket", "ScriptingIntegerSocket"): "int({value})",
    (
        "ScriptingVectorSocket",
        "ScriptingIntegerSocket",
    ): "(int({value}[0]) if hasattr({value}, '__getitem__') else 0)",
    (
        "ScriptingColorSocket",
        "ScriptingIntegerSocket",
    ): "(int({value}[0]) if hasattr({value}, '__getitem__') else 0)",
    (
        "ScriptingDataSocket",
        "ScriptingIntegerSocket",
    ): "(int({value}) if isinstance({value}, (int, float, bool)) else 0)",
    ("ScriptingBlendDataSocket", "ScriptingIntegerSocket"): None,
    # To Vector
    ("ScriptingStringSocket", "ScriptingVectorSocket"): "(0.0, 0.0, 0.0)",
    (
        "ScriptingBooleanSocket",
        "ScriptingVectorSocket",
    ): "((1.0, 1.0, 1.0) if {value} else (0.0, 0.0, 0.0))",
    ("ScriptingFloatSocket", "ScriptingVectorSocket"): "({value}, {value}, {value})",
    ("ScriptingIntegerSocket", "ScriptingVectorSocket"): "({value}, {value}, {value})",
    (
        "ScriptingColorSocket",
        "ScriptingVectorSocket",
    ): "(({value}[0], {value}[1], {value}[2]) if hasattr({value}, '__getitem__') and len({value}) >= 3 else (0.0, 0.0, 0.0))",
    (
        "ScriptingDataSocket",
        "ScriptingVectorSocket",
    ): "({value} if hasattr({value}, '__getitem__') and len({value}) >= 3 else (0.0, 0.0, 0.0))",
    ("ScriptingBlendDataSocket", "ScriptingVectorSocket"): None,
    # To Color
    ("ScriptingStringSocket", "ScriptingColorSocket"): "(1.0, 1.0, 1.0, 1.0)",
    (
        "ScriptingBooleanSocket",
        "ScriptingColorSocket",
    ): "((1.0, 1.0, 1.0, 1.0) if {value} else (0.0, 0.0, 0.0, 1.0))",
    (
        "ScriptingFloatSocket",
        "ScriptingColorSocket",
    ): "({value}, {value}, {value}, 1.0)",
    (
        "ScriptingIntegerSocket",
        "ScriptingColorSocket",
    ): "({value}, {value}, {value}, 1.0)",
    (
        "ScriptingVectorSocket",
        "ScriptingColorSocket",
    ): "(({value}[0], {value}[1], {value}[2], 1.0) if hasattr({value}, '__getitem__') and len({value}) >= 3 else (0.0, 0.0, 0.0, 1.0))",
    (
        "ScriptingDataSocket",
        "ScriptingColorSocket",
    ): "({value} if hasattr({value}, '__getitem__') and len({value}) >= 4 else (0.0, 0.0, 0.0, 1.0))",
    ("ScriptingBlendDataSocket", "ScriptingColorSocket"): None,
    # To Data (generic - no conversion needed, just pass through)
    ("ScriptingStringSocket", "ScriptingDataSocket"): "{value}",
    ("ScriptingBooleanSocket", "ScriptingDataSocket"): "{value}",
    ("ScriptingFloatSocket", "ScriptingDataSocket"): "{value}",
    ("ScriptingIntegerSocket", "ScriptingDataSocket"): "{value}",
    ("ScriptingVectorSocket", "ScriptingDataSocket"): "{value}",
    ("ScriptingColorSocket", "ScriptingDataSocket"): "{value}",
    ("ScriptingBlendDataSocket", "ScriptingDataSocket"): "{value}",
    # To BlendData (pass through from data, plain values can't be data)
    ("ScriptingDataSocket", "ScriptingBlendDataSocket"): "{value}",
    ("ScriptingStringSocket", "ScriptingBlendDataSocket"): None,
    ("ScriptingBooleanSocket", "ScriptingBlendDataSocket"): None,
    ("ScriptingFloatSocket", "ScriptingBlendDataSocket"): None,
    ("ScriptingIntegerSocket", "ScriptingBlendDataSocket"): None,
    ("ScriptingVectorSocket", "ScriptingBlendDataSocket"): None,
    ("ScriptingColorSocket", "ScriptingBlendDataSocket"): None,
    ("ScriptingListSocket", "ScriptingBlendDataSocket"): None,
    # To List
    ("ScriptingStringSocket", "ScriptingListSocket"): "list({value})",
    ("ScriptingBooleanSocket", "ScriptingListSocket"): "[{value}]",
    ("ScriptingFloatSocket", "ScriptingListSocket"): "[{value}]",
    ("ScriptingIntegerSocket", "ScriptingListSocket"): "[{value}]",
    ("ScriptingVectorSocket", "ScriptingListSocket"): "list({value})",
    ("ScriptingColorSocket", "ScriptingListSocket"): "list({value})",
    (
        "ScriptingDataSocket",
        "ScriptingListSocket",
    ): "({value} if isinstance({value}, list) else [{value}])",
    ("ScriptingBlendDataSocket", "ScriptingListSocket"): "[{value}]",
    # From List to other types
    ("ScriptingListSocket", "ScriptingStringSocket"): "str({value})",
    ("ScriptingListSocket", "ScriptingBooleanSocket"): "bool({value})",
    (
        "ScriptingListSocket",
        "ScriptingFloatSocket",
    ): "(float({value}[0]) if {value} else 0.0)",
    (
        "ScriptingListSocket",
        "ScriptingIntegerSocket",
    ): "(int({value}[0]) if {value} else 0)",
    (
        "ScriptingListSocket",
        "ScriptingVectorSocket",
    ): "(tuple({value}[:3]) if len({value}) >= 3 else (0.0, 0.0, 0.0))",
    (
        "ScriptingListSocket",
        "ScriptingColorSocket",
    ): "(tuple({value}[:4]) if len({value}) >= 4 else (0.0, 0.0, 0.0, 1.0))",
    ("ScriptingListSocket", "ScriptingDataSocket"): "{value}",
    # Icons are icon ids (ints); names of built-in icons are looked up when
    # the code runs ({icon_id}: the helper, see HELPERS below)
    ("ScriptingIntegerSocket", "ScriptingIconSocket"): "{value}",
    ("ScriptingStringSocket", "ScriptingIconSocket"): "{icon_id}({value})",
    ("ScriptingDataSocket", "ScriptingIconSocket"): "{icon_id}({value})",
    ("ScriptingIconSocket", "ScriptingIntegerSocket"): "{value}",
    ("ScriptingIconSocket", "ScriptingDataSocket"): "{value}",
    ("ScriptingIconSocket", "ScriptingBooleanSocket"): "bool({value})",
    ("ScriptingIconSocket", "ScriptingListSocket"): "[{value}]",
    **{
        (other, "ScriptingIconSocket"): None
        for other in (
            "ScriptingBooleanSocket",
            "ScriptingFloatSocket",
            "ScriptingVectorSocket",
            "ScriptingColorSocket",
            "ScriptingBlendDataSocket",
            "ScriptingListSocket",
        )
    },
    **{
        ("ScriptingIconSocket", other): None
        for other in (
            "ScriptingStringSocket",
            "ScriptingFloatSocket",
            "ScriptingVectorSocket",
            "ScriptingColorSocket",
            "ScriptingBlendDataSocket",
        )
    },
}

# helpers (core/helpers.py) conversion templates call, by placeholder
HELPERS = ("icon_id", "as_text")


class ConversionError(ValueError):
    """A value of one socket type can't be used as another."""

    def __init__(self, from_socket_type, to_socket_type):
        from .socket_types import DATA_SOCKET_LABELS

        self.from_label = DATA_SOCKET_LABELS.get(from_socket_type, from_socket_type)
        self.to_label = DATA_SOCKET_LABELS.get(to_socket_type, to_socket_type)
        super().__init__(f"{self.from_label} can't be used as {self.to_label}")


def get_conversion(
    from_socket_type: str, to_socket_type: str, value_code: str, helper=None
) -> str:
    """
    Get the converted code for a value going from one socket type to another.

    Args:
        from_socket_type: The bl_idname of the source socket
        to_socket_type: The bl_idname of the target socket
        value_code: The code string representing the value to convert
        helper: name -> call name of a helper, for templates using one

    Returns:
        The converted code string, or the original value_code if no conversion needed
    """
    # Same type - no conversion needed
    if from_socket_type == to_socket_type:
        return value_code
    # a value of any type that's clearly of the type already: `[...]`
    if from_socket_type == "ScriptingDataSocket" and is_of_type(
        value_code, to_socket_type
    ):
        return value_code

    # Look up conversion
    conversion_key = (from_socket_type, to_socket_type)
    if conversion_key in CONVERSIONS:
        template = CONVERSIONS[conversion_key]
        if template is None:
            raise ConversionError(from_socket_type, to_socket_type)
        for name in HELPERS:
            if "{" + name + "}" in template:
                template = template.replace("{" + name + "}", helper(name))
        if template.count("{value}") > 1 and not is_simple(value_code):
            # evaluate the source expression only once (it may have side
            # effects or be expensive)
            return f"(lambda _sn_v: {template.format(value='_sn_v')})({value_code})"
        return template.format(value=parenthesize(value_code))

    # No conversion found - return as-is (may cause runtime errors if incompatible)
    return value_code


_STRING_METHODS = {"join", "format", "lower", "upper", "strip", "replace", "title"}
_BOOLEAN_CALLS = {"bool", "isinstance", "hasattr", "callable", "any", "all"}


def is_of_type(code: str, socket_type: str) -> bool:
    """`code` is an expression that can only give a value of `socket_type`
    (a list display, a comparison, ...): a conversion would only add noise."""
    try:
        node = ast.parse(code.strip(), mode="eval").body
    except SyntaxError:
        return False
    call = node.func if isinstance(node, ast.Call) else None
    called = getattr(call, "id", None) or getattr(call, "attr", None)
    if socket_type == "ScriptingListSocket":
        return isinstance(node, (ast.List, ast.ListComp)) or (
            isinstance(call, ast.Name) and called in ("list", "sorted")
        )
    if socket_type == "ScriptingStringSocket":
        if isinstance(node, ast.Constant):
            return isinstance(node.value, str)
        if isinstance(node, ast.JoinedStr):
            return True
        if isinstance(call, ast.Name):
            return called in ("str", "repr")
        return isinstance(call, ast.Attribute) and called in _STRING_METHODS
    if socket_type == "ScriptingBooleanSocket":
        if isinstance(node, ast.Constant):
            return isinstance(node.value, bool)
        if isinstance(node, (ast.Compare, ast.BoolOp)):
            return True
        if isinstance(node, ast.UnaryOp):
            return isinstance(node.op, ast.Not)
        return isinstance(call, ast.Name) and called in _BOOLEAN_CALLS
    if socket_type == "ScriptingIntegerSocket":
        if isinstance(node, ast.Constant):
            return type(node.value) is int
        return isinstance(call, ast.Name) and called in ("int", "len", "round")
    if socket_type == "ScriptingFloatSocket":
        if isinstance(node, ast.Constant):
            return type(node.value) in (int, float)
        return isinstance(call, ast.Name) and called in ("float", "int", "len")
    return False
