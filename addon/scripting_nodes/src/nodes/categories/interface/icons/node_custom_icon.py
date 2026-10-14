import bpy

from .....core.context import NodeError
from .....sockets.spec import Icon
from ...._icon import image_file
from ....base_node import ScriptingBaseNode


class SNA_Node_CustomIcon(ScriptingBaseNode, bpy.types.Node):
    """An image as icon. The image file ships with the add-on (in `icons/`):
    pack the image or keep its file next to the .blend."""

    bl_idname = "SNA_Node_CustomIcon"
    bl_label = "Custom Icon"
    bl_width_default = 200
    sn_outputs = [Icon("icon", "Icon")]

    image: bpy.props.PointerProperty(type=bpy.types.Image, name="Image")

    def draw(self, context, layout):
        layout.template_ID(self, "image", open="image.open")
        if self.image is not None:
            layout.template_icon(layout.icon(self.image), scale=2)

    def emit(self, ctx):
        if self.image is None:
            raise NodeError("Pick an image")
        name, data = image_file(self.image)
        rel = ctx.asset(f"icons/{name}", data)
        file = rel.split("/", 1)[1]
        ctx.output("icon", f"{ctx.helper('sn_custom_icon')}({file!r})")
