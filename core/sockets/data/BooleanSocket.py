import bpy

from ..base_socket import ScriptingSocket


class SNA_BooleanSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SNA_BooleanSocket"
    bl_label = "Boolean"

    value: bpy.props.BoolProperty(
        default=False, update=lambda self, _: self.node.mark_dirty()
    )

    def _python_value(self):
        if self.is_output:
            return self.code if self.code else "False"
        return str(self.value)

    def get_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return (0.95, 0.73, 1, 1)

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


class SNA_BooleanSocketInterface(bpy.types.NodeTreeInterfaceSocket):

    bl_idname = "SNA_BooleanSocketInterface"
    bl_socket_idname = "SNA_BooleanSocket"
    bl_label = "Boolean"

    def draw(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        layout.label(text="drawing")


def register():
    bpy.utils.register_class(SNA_BooleanSocketInterface)


def unregister():
    bpy.utils.unregister_class(SNA_BooleanSocketInterface)
