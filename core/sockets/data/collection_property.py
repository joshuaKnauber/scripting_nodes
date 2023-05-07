import bpy
from ..base_socket import ScriptingSocket


class SN_CollectionPropertySocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_CollectionPropertySocket"

    def get_color(self, context, node):
        return (0, 0.87, 0.7)
