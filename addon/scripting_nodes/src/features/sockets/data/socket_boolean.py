from ..base_socket import ScriptingBaseSocket
import bpy


class ScriptingBooleanSocket(ScriptingBaseSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingBooleanSocket"
    bl_label = "Boolean"

    def update_value(self, context):
        self.node._generate()

    value: bpy.props.BoolProperty(default=True, update=update_value)

    def _to_code(self):
        return f"{self.value}"

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "value", text=self.name)

    @classmethod
    def draw_color_simple(cls):
        return (1, 0, 0, 1)
