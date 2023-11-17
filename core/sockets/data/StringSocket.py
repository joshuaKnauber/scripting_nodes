import bpy

from ..base_socket import ScriptingSocket


class SNA_StringSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SNA_StringSocket"

    value: bpy.props.StringProperty(
        default="",
        update=lambda self, _: self.node.mark_dirty(),
        options={"TEXTEDIT_UPDATE"},
    )

    def _python_value(self):
        if self.is_output:
            return self.code if self.code else "''"
        value = self.value.replace("'", "\\'")
        return f"'{value}'"

    def get_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return (0.44, 0.7, 1, 1)

    def draw_socket(self, context, layout, node, text):
        if not self.is_output:
            if self.show_enable:
                layout.prop(
                    self,
                    "enabled",
                    text="",
                    icon="HIDE_OFF" if self.enabled else "HIDE_ON",
                    emboss=False,
                )
            if self.enabled:
                layout.prop(self, "value", text=text)
            else:
                layout.label(text=text)
        else:
            layout.label(text=text)
