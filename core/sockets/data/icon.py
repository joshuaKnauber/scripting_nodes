import bpy
from ..base_socket import ScriptingSocket


class SN_IconSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_IconSocket"

    def get_color(self, context, node):
        return (1, 0.4, 0.2)
