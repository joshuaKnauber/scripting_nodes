"""The data socket types, in one table. Icons, enum items and id lists used
across the addon are all derived from it."""

from typing import Literal

# (bl_idname, label, icon, description)
DATA_SOCKETS = [
    ("ScriptingDataSocket", "Data", "MOD_DATA_TRANSFER", "Any value"),
    ("ScriptingBlendDataSocket", "Blend Data", "BLENDER", "Blend data (Scene, Object, ...)"),
    ("ScriptingStringSocket", "String", "SYNTAX_OFF", "Text"),
    ("ScriptingBooleanSocket", "Boolean", "CHECKBOX_HLT", "True or False"),
    ("ScriptingFloatSocket", "Float", "CON_TRANSLIKE", "Decimal number"),
    ("ScriptingIntegerSocket", "Integer", "CON_TRANSFORM", "Whole number"),
    ("ScriptingVectorSocket", "Vector", "EMPTY_AXIS", "2 to 4 numbers"),
    ("ScriptingColorSocket", "Color", "COLOR", "RGB(A) color"),
    ("ScriptingListSocket", "List", "OUTLINER_OB_GROUP_INSTANCE", "List of values"),
]  # fmt: skip

FLOW_SOCKET = "ScriptingFlowSocket"

DATA_SOCKET_IDNAMES = [idname for idname, *_ in DATA_SOCKETS]
DATA_SOCKET_ICONS = {idname: icon for idname, _, icon, _ in DATA_SOCKETS}
DATA_SOCKET_LABELS = {idname: label for idname, label, *_ in DATA_SOCKETS}
DATA_SOCKET_ENUM_ITEMS = [
    (idname, label, description, icon, i)
    for i, (idname, label, icon, description) in enumerate(DATA_SOCKETS)
]

SOCKET_IDNAME_TYPE = Literal[
    "ScriptingFlowSocket",
    "ScriptingDataSocket",
    "ScriptingBlendDataSocket",
    "ScriptingStringSocket",
    "ScriptingBooleanSocket",
    "ScriptingFloatSocket",
    "ScriptingIntegerSocket",
    "ScriptingVectorSocket",
    "ScriptingColorSocket",
    "ScriptingListSocket",
]
