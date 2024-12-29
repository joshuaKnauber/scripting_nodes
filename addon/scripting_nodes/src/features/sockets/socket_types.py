from typing import Literal


# icon -> (1, .56, .46, 1)
# blend -> (0, .85, .53, 1)


SOCKET_IDNAMES = Literal[
    "ScriptingInterfaceSocket",
    "ScriptingLogicSocket",
    "ScriptingProgramSocket",
    "ScriptingStringSocket",
    "ScriptingBooleanSocket",
    "ScriptingFloatSocket",
    "ScriptingIntegerSocket",
]
