import bpy
from ..base_socket import ScriptingSocket


class SN_BooleanSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_BooleanSocket"

    def get_color(self, context, node):
        return (0.95, 0.73, 1)
