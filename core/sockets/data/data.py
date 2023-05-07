import bpy
from ..base_socket import ScriptingSocket


class SN_DataSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_DataSocket"

    def get_color(self, context, node):
        return (0.3, 0.3, 0.3)
