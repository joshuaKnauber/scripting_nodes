import bpy
from ..base_socket import ScriptingSocket


class SN_FloatVectorSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_FloatVectorSocket"

    def get_color(self, context, node):
        # return (0.93, 0.85, 0.25)
        return (0.38, 0.34, 0.84)
