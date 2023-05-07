import bpy
from ..base_socket import ScriptingSocket


class SN_IntegerSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_IntegerSocket"

    def get_color(self, context, node):
        return (0.15, 0.52, 0.17)
