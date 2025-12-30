from typing import Literal


# icon -> (1, .56, .46, 1)
# blend -> (0, .85, .53, 1)
# list -> ()
# dict -> ()


SOCKET_IDNAME_TYPE = Literal[
    "ScriptingInterfaceSocket",
    "ScriptingLogicSocket",
    "ScriptingProgramSocket",
    "ScriptingDataSocket",
    "ScriptingBlendDataSocket",
    "ScriptingStringSocket",
    "ScriptingBooleanSocket",
    "ScriptingFloatSocket",
    "ScriptingIntegerSocket",
    "ScriptingVectorSocket",
    "ScriptingColorSocket",
]

DATA_SOCKET_ICONS = {
    "ScriptingDataSocket": "MOD_DATA_TRANSFER",
    "ScriptingBlendDataSocket": "BLENDER",
    "ScriptingStringSocket": "SYNTAX_OFF",
    "ScriptingBooleanSocket": "CHECKBOX_HLT",
    "ScriptingFloatSocket": "CON_TRANSLIKE",
    "ScriptingIntegerSocket": "CON_TRANSFORM",
    "ScriptingVectorSocket": "EMPTY_AXIS",
    "ScriptingColorSocket": "COLOR",
}

DATA_SOCKET_IDNAMES = [
    "ScriptingDataSocket",
    "ScriptingBlendDataSocket",
    "ScriptingStringSocket",
    "ScriptingBooleanSocket",
    "ScriptingFloatSocket",
    "ScriptingIntegerSocket",
    "ScriptingVectorSocket",
    "ScriptingColorSocket",
]

DATA_SOCKET_ENUM_ITEMS = [
    (
        "ScriptingDataSocket",
        "Data",
        "Data",
        DATA_SOCKET_ICONS["ScriptingDataSocket"],
        0,
    ),
    (
        "ScriptingBlendDataSocket",
        "Blend Data",
        "Blend Data (Scene, Object, etc.)",
        DATA_SOCKET_ICONS["ScriptingBlendDataSocket"],
        1,
    ),
    (
        "ScriptingStringSocket",
        "String",
        "String",
        DATA_SOCKET_ICONS["ScriptingStringSocket"],
        2,
    ),
    (
        "ScriptingBooleanSocket",
        "Boolean",
        "Boolean",
        DATA_SOCKET_ICONS["ScriptingBooleanSocket"],
        3,
    ),
    (
        "ScriptingFloatSocket",
        "Float",
        "Float",
        DATA_SOCKET_ICONS["ScriptingFloatSocket"],
        4,
    ),
    (
        "ScriptingIntegerSocket",
        "Integer",
        "Integer",
        DATA_SOCKET_ICONS["ScriptingIntegerSocket"],
        5,
    ),
    (
        "ScriptingVectorSocket",
        "Vector",
        "Vector",
        DATA_SOCKET_ICONS["ScriptingVectorSocket"],
        6,
    ),
    (
        "ScriptingColorSocket",
        "Color",
        "Color",
        DATA_SOCKET_ICONS["ScriptingColorSocket"],
        7,
    ),
]
