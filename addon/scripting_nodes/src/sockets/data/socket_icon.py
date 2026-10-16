import bpy

from ...lib.icons import draw_icon_picker
from ..base_socket import ScriptingBaseSocket


class ScriptingIconSocket(ScriptingBaseSocket):
    """An icon. Its value in generated code is an icon id (`icon_value`), so
    built-in icons and custom ones (previews) are the same; 0 is no icon.

    The socket's own value is a built-in icon's name ("" = none). Nodes that
    draw it use nodes/_icon.icon_argument: `icon='NAME'` for a picked icon,
    `icon_value=...` for a connected one.
    """

    bl_idname = "ScriptingIconSocket"
    bl_label = "Icon"
    color = (0.95, 0.55, 0.75, 1)

    value: bpy.props.StringProperty(update=ScriptingBaseSocket.update_value)

    def literal(self):
        return "0"

    def literal_code(self, ctx):
        if not self.value:
            return "0"
        return f"{ctx.helper('icon_id')}({self.value!r})"

    def draw_value(self, context, layout, text):
        row = layout.row(align=True)
        if text:
            row.label(text=text)
        draw_icon_picker(row, self, "value")
