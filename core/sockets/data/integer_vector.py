import bpy
from ..base_socket import ScriptingSocket


class SN_IntegerVectorSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_IntegerVectorSocket"

    def get_color(self, context, node):
        return (0.38, 0.34, 0.84)
