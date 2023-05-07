import bpy
from ..base_socket import ScriptingSocket


class SN_StringSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_StringSocket"

    def get_color(self, context, node):
        return (0.44, 0.7, 1)
