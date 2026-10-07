import bpy

from ..base_socket import ScriptingBaseSocket


class ScriptingFloatSocket(ScriptingBaseSocket):
    bl_idname = "ScriptingFloatSocket"
    bl_label = "Float"
    color = (0.65, 0.65, 0.65, 1)

    value: bpy.props.FloatProperty(default=0.0, update=ScriptingBaseSocket.update_value)

    def literal(self):
        return repr(float(self.value))

    def draw_value(self, context, layout, text):
        layout.prop(self, "value", text=text)
