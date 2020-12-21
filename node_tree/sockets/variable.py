import bpy
from .base_sockets import ScriptingSocket, DynamicSocket
from ...compiler.compiler import process_node



class SN_DynamicVariableSocket(bpy.types.NodeSocket, DynamicSocket):
    connects_to = ["SN_StringSocket", "SN_DataSocket","SN_BooleanSocket","SN_FloatSocket","SN_IntSocket"]
    make_variable = True
    add_idname = "SN_DataSocket"