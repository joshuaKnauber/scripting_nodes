from operator import is_

import bpy

from ..base_socket import ScriptingSocket

DATA_DEFAULTS = {
    "Scene": {
        "data": "bpy.context.scene",
        "label": "Active"
    },
    "Object": {
        "data": "bpy.context.object",
        "label": "Active"
    },
}


class SN_PropertySocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_PropertySocket"

    # Can have meta of type -> Type of data, identifier -> property identifier, data -> property parent data

    def _python_value(self):
        if self.is_output:
            return self.code if self.code else "None"
        # return default value for data type if set
        data_type = self.get_meta("type")
        if data_type in DATA_DEFAULTS:
            return DATA_DEFAULTS[data_type]["data"]
        return "None"

    def get_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return (0, 0.87, 0.7, 1)

    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)
