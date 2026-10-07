import bpy

from ..base_socket import ScriptingBaseSocket


class ScriptingBooleanSocket(ScriptingBaseSocket):
    bl_idname = "ScriptingBooleanSocket"
    bl_label = "Boolean"
    color = (0.9, 0.7, 1, 1)

    value: bpy.props.BoolProperty(
        default=False, update=ScriptingBaseSocket.update_value
    )

    def literal(self):
        return repr(bool(self.value))

    def draw_value(self, context, layout, text):
        layout.prop(self, "value", text=text)
