"""
Socket type conversion utilities.

This module provides automatic conversion between different data socket types.
When a socket of one type is connected to a socket of a different type,
the appropriate conversion wrapper is applied to the generated code.
"""

# Conversion functions for each target type
# Format: (from_type, to_type) -> conversion_template
# The template uses {value} as a placeholder for the source code

CONVERSIONS = {
    # To String
    ("ScriptingBooleanSocket", "ScriptingStringSocket"): "str({value})",
    ("ScriptingFloatSocket", "ScriptingStringSocket"): "str({value})",
    ("ScriptingIntegerSocket", "ScriptingStringSocket"): "str({value})",
    ("ScriptingVectorSocket", "ScriptingStringSocket"): "str({value})",
    ("ScriptingColorSocket", "ScriptingStringSocket"): "str({value})",
    ("ScriptingDataSocket", "ScriptingStringSocket"): "str({value})",
    ("ScriptingBlendDataSocket", "ScriptingStringSocket"): "str({value})",
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
    ("ScriptingIntegerSocket", "ScriptingFloatSocket"): "float({value})",
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
    ("ScriptingBlendDataSocket", "ScriptingFloatSocket"): "0.0",
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
    ("ScriptingBlendDataSocket", "ScriptingIntegerSocket"): "0",
    # To Vector
    ("ScriptingStringSocket", "ScriptingVectorSocket"): "(0.0, 0.0, 0.0)",
    (
        "ScriptingBooleanSocket",
        "ScriptingVectorSocket",
    ): "((1.0, 1.0, 1.0) if {value} else (0.0, 0.0, 0.0))",
    ("ScriptingFloatSocket", "ScriptingVectorSocket"): "({value}, {value}, {value})",
    (
        "ScriptingIntegerSocket",
        "ScriptingVectorSocket",
    ): "(float({value}), float({value}), float({value}))",
    (
        "ScriptingColorSocket",
        "ScriptingVectorSocket",
    ): "(({value}[0], {value}[1], {value}[2]) if hasattr({value}, '__getitem__') and len({value}) >= 3 else (0.0, 0.0, 0.0))",
    (
        "ScriptingDataSocket",
        "ScriptingVectorSocket",
    ): "({value} if hasattr({value}, '__getitem__') and len({value}) >= 3 else (0.0, 0.0, 0.0))",
    ("ScriptingBlendDataSocket", "ScriptingVectorSocket"): "(0.0, 0.0, 0.0)",
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
    ): "(float({value}), float({value}), float({value}), 1.0)",
    (
        "ScriptingVectorSocket",
        "ScriptingColorSocket",
    ): "(({value}[0], {value}[1], {value}[2], 1.0) if hasattr({value}, '__getitem__') and len({value}) >= 3 else (0.0, 0.0, 0.0, 1.0))",
    (
        "ScriptingDataSocket",
        "ScriptingColorSocket",
    ): "({value} if hasattr({value}, '__getitem__') and len({value}) >= 4 else (0.0, 0.0, 0.0, 1.0))",
    ("ScriptingBlendDataSocket", "ScriptingColorSocket"): "(0.0, 0.0, 0.0, 1.0)",
    # To Data (generic - no conversion needed, just pass through)
    ("ScriptingStringSocket", "ScriptingDataSocket"): "{value}",
    ("ScriptingBooleanSocket", "ScriptingDataSocket"): "{value}",
    ("ScriptingFloatSocket", "ScriptingDataSocket"): "{value}",
    ("ScriptingIntegerSocket", "ScriptingDataSocket"): "{value}",
    ("ScriptingVectorSocket", "ScriptingDataSocket"): "{value}",
    ("ScriptingColorSocket", "ScriptingDataSocket"): "{value}",
    ("ScriptingBlendDataSocket", "ScriptingDataSocket"): "{value}",
    # To BlendData (pass through from data types, others become None)
    ("ScriptingDataSocket", "ScriptingBlendDataSocket"): "{value}",
    ("ScriptingStringSocket", "ScriptingBlendDataSocket"): "None",
    ("ScriptingBooleanSocket", "ScriptingBlendDataSocket"): "None",
    ("ScriptingFloatSocket", "ScriptingBlendDataSocket"): "None",
    ("ScriptingIntegerSocket", "ScriptingBlendDataSocket"): "None",
    ("ScriptingVectorSocket", "ScriptingBlendDataSocket"): "None",
    ("ScriptingColorSocket", "ScriptingBlendDataSocket"): "None",
}


def get_conversion(from_socket_type: str, to_socket_type: str, value_code: str) -> str:
    """
    Get the converted code for a value going from one socket type to another.

    Args:
        from_socket_type: The bl_idname of the source socket
        to_socket_type: The bl_idname of the target socket
        value_code: The code string representing the value to convert

    Returns:
        The converted code string, or the original value_code if no conversion needed
    """
    # Same type - no conversion needed
    if from_socket_type == to_socket_type:
        return value_code

    # Look up conversion
    conversion_key = (from_socket_type, to_socket_type)
    if conversion_key in CONVERSIONS:
        template = CONVERSIONS[conversion_key]
        return template.format(value=value_code)

    # No conversion found - return as-is (may cause runtime errors if incompatible)
    return value_code
