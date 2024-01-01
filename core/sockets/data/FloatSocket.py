import bpy

from ..base_socket import ScriptingSocket


class SNA_FloatSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SNA_FloatSocket"
    bl_label = "Float"

    value: bpy.props.FloatProperty(
        default=0.0, update=lambda self, _: self.node.mark_dirty()
    )

    def _python_value(self):
        if self.is_output:
            return self.code if self.code else "0.0"
        return str(self.value)

    def get_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return (0.5, 0.5, 0.5, 1)

    def draw_socket(self, context, layout, node, text):
        if not self.is_output:
            if self.show_editable:
                layout.prop(
                    self,
                    "editable",
                    text="",
                    icon="HIDE_OFF" if self.editable else "HIDE_ON",
                    emboss=False,
                )
            if self.editable and not self.is_linked:
                layout.prop(self, "value", text=text)
            else:
                layout.label(text=text)
        else:
            layout.label(text=text)
