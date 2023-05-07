import bpy
from ..base_socket import ScriptingSocket


class SN_ListSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_ListSocket"

    def get_color(self, context, node):
        return (0.85, 0.15, 1)
