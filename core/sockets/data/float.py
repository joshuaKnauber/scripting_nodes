import bpy
from ..base_socket import ScriptingSocket


class SN_FloatSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_FloatSocket"

    def get_color(self, context, node):
        return (0.6, 0.6, 0.6)
