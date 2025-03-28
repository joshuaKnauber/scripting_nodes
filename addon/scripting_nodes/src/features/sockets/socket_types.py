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
    "ScriptingStringSocket",
    "ScriptingBooleanSocket",
    "ScriptingFloatSocket",
    "ScriptingIntegerSocket",
    "ScriptingVectorSocket",
    "ScriptingColorSocket",
    "ScriptingListSocket",
]

DATA_SOCKET_ICONS = {
    "ScriptingDataSocket": "MOD_DATA_TRANSFER",
    "ScriptingStringSocket": "SYNTAX_OFF",
    "ScriptingBooleanSocket": "CHECKBOX_HLT",
    "ScriptingFloatSocket": "CON_TRANSLIKE",
    "ScriptingIntegerSocket": "CON_TRANSFORM",
    "ScriptingVectorSocket": "EMPTY_AXIS",
    "ScriptingColorSocket": "COLOR",
    "ScriptingListSocket": "LONGDISPLAY",
}

DATA_SOCKET_IDNAMES = [
    "ScriptingDataSocket",
    "ScriptingStringSocket",
    "ScriptingBooleanSocket",
    "ScriptingFloatSocket",
    "ScriptingIntegerSocket",
    "ScriptingVectorSocket",
    "ScriptingColorSocket",
    "ScriptingListSocket",
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
        "ScriptingStringSocket",
        "String",
        "String",
        DATA_SOCKET_ICONS["ScriptingStringSocket"],
        1,
    ),
    (
        "ScriptingBooleanSocket",
        "Boolean",
        "Boolean",
        DATA_SOCKET_ICONS["ScriptingBooleanSocket"],
        2,
    ),
    (
        "ScriptingFloatSocket",
        "Float",
        "Float",
        DATA_SOCKET_ICONS["ScriptingFloatSocket"],
        3,
    ),
    (
        "ScriptingIntegerSocket",
        "Integer",
        "Integer",
        DATA_SOCKET_ICONS["ScriptingIntegerSocket"],
        4,
    ),
    (
        "ScriptingVectorSocket",
        "Vector",
        "Vector",
        DATA_SOCKET_ICONS["ScriptingVectorSocket"],
        5,
    ),
    (
        "ScriptingColorSocket",
        "Color",
        "Color",
        DATA_SOCKET_ICONS["ScriptingColorSocket"],
        6,
    ),
    (
        "ScriptingListSocket",
        "List",
        "List",
        DATA_SOCKET_ICONS["ScriptingListSocket"],
        7,
    ),
]
