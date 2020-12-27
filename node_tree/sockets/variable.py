import bpy
from .base_sockets import ScriptingSocket, DynamicSocket
from ...compiler.compiler import process_node



class SN_DynamicVariableSocket(bpy.types.NodeSocket, DynamicSocket):
    make_variable = True
    add_idname = "SN_DataSocket"
    copy_type = True