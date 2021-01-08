import bpy
from .base_sockets import ScriptingSocket
from ...compiler.compiler import process_node



class SN_DynamicVariableSocket(bpy.types.NodeSocket, ScriptingSocket):

    group = "DATA"
    bl_label = "Variable"
    socket_type = "VARIABLE"
    
    dynamic = True
    copy_socket = True
    to_add_idname = "SN_DataSocket"