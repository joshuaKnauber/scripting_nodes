import bpy

from ..base_socket import ScriptingSocket


class SN_StringSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_StringSocket"

    value: bpy.props.StringProperty(default="", update=lambda self, _: self.node.mark_dirty(), options={"TEXTEDIT_UPDATE"})

    def python_value(self):
        if self.is_output:
            return self.code if self.code else "''"
        value = self.value.replace('\'', '\\\'')
        return f"'{value}'"

    def get_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return (0.44, 0.7, 1, 1)

    def draw_socket(self, context, layout, node, text):
        if not self.is_output:
            layout.prop(self, "value", text="" if self.is_output else text)
        else:
            layout.label(text=text)
