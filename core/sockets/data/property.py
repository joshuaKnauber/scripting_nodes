import bpy
from ..base_socket import ScriptingSocket


class SN_PropertySocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_PropertySocket"

    def get_color(self, context, node):
        return (0, 0.87, 0.7)
