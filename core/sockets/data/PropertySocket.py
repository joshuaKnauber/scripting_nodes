import bpy

from ..base_socket import ScriptingSocket

DATA_DEFAULTS = {
    "Scene": {"data": "bpy.context.scene", "label": "Using Active"},
    "Object": {"data": "bpy.context.object", "label": "Using Active"},
}


class SNA_PropertySocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SNA_PropertySocket"
    bl_label = "Property"

    # Can have optional meta of
    # - parent: path to the parent data of the property
    # - identifier: identifier of the property
    # - type: type of the property

    def _python_value(self):
        if self.is_output:
            return self.code if self.code else "None"
        # return default value for data type if set
        data_type = self.get_meta("type", "")
        if data_type in DATA_DEFAULTS:
            return DATA_DEFAULTS[data_type]["data"]
        return "None"

    def get_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return (0, 0.87, 0.7, 1)

    def draw_socket(self, context, layout, node, text):
        if not self.is_output and not self.is_linked:
            data_type = self.get_meta("type", "")
            if data_type in DATA_DEFAULTS:
                text = f"{text} ({DATA_DEFAULTS[data_type]['label']})"
            elif data_type:
                text = f"{text} (No Default)"
        layout.label(text=text)
