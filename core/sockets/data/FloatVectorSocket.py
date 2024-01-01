from cProfile import label
import bpy

from ..base_socket import ScriptingSocket


class SNA_FloatVectorSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SNA_FloatVectorSocket"
    bl_label = "Float Vector"

    value: bpy.props.FloatVectorProperty(
        size=32,
        update=lambda self, _: self.node.mark_dirty(),
    )

    size: bpy.props.IntProperty(default=3)

    labels: bpy.props.StringProperty(default="")

    def _python_value(self):
        if self.is_output:
            return (
                self.code if self.code else "(" + ", ".join(["0.0"] * self.size) + ")"
            )
        values = [str(v) for v in self.value]
        return "(" + ", ".join(values[: self.size]) + ")"

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
                col = layout.column(align=True, heading=text)
                labels = self.labels.split(",")
                for i in range(self.size):
                    col.prop(
                        self,
                        "value",
                        index=i,
                        text="" if i >= len(labels) else labels[i],
                    )
            else:
                layout.label(text=text)
        else:
            layout.label(text=text)
