import bpy

from ..base_socket import ScriptingSocket


class SNA_IconSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SNA_IconSocket"
    bl_label = "Icon"

    value: bpy.props.IntProperty(
        default=0, update=lambda self, _: self.node.mark_dirty()
    )

    value_named: bpy.props.StringProperty(
        default="", update=lambda self, _: self.node.mark_dirty()
    )

    def _python_value(self):
        if self.is_output:
            return self.code if self.code else "icon_value=0"
        return (
            f"icon='{self.value_named}'"
            if self.value_named
            else f"icon_value={self.value}"
        )

    def get_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return (1, 0.4, 0.2, 1)

    def draw_socket(self, context, layout, node, text):
        if not self.is_output:
            if not self.is_linked:
                if self.value_named:
                    op = layout.operator(
                        "sna.select_icon", text="Icon", icon=self.value_named
                    )
                else:
                    op = layout.operator(
                        "sna.select_icon",
                        text="Icon",
                        icon_value=self.value,
                    )
                op.node = self.node.id
                op.socket = self.index
            else:
                layout.label(text=text)
        else:
            layout.label(text=text)
