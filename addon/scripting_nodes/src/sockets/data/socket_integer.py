import bpy

from ..base_socket import ScriptingBaseSocket


class ScriptingIntegerSocket(ScriptingBaseSocket):
    bl_idname = "ScriptingIntegerSocket"
    bl_label = "Integer"
    color = (0.32, 0.65, 0.35, 1)

    value: bpy.props.IntProperty(default=0, update=ScriptingBaseSocket.update_value)

    def literal(self):
        return repr(int(self.value))

    def draw_value(self, context, layout, text):
        layout.prop(self, "value", text=text)
