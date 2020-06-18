import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons
from random import randint


class SN_Label(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_Label"
    bl_label = "Label"
    bl_icon = node_icons["INTERFACE"]

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.inputs.new("SN_StringSocket", "Text").value = "New Label"

        self.outputs.new("SN_LayoutSocket", "Layout")

    icon: bpy.props.StringProperty(default="")

    def draw_buttons(self, context, layout):
        self.draw_icon_chooser(layout)

    def evaluate(self, output):
        error_list = []

        layout_type, errors = self.SocketHandler.get_layout_type(self.outputs[0])
        error_list += errors

        text_input, errors = self.SocketHandler.socket_value(self.inputs[0])
        error_list += errors

        icon = []
        if self.icon:
            icon = [",icon=\""+self.icon+"\""]

        return {
            "blocks": [
                {
                    "lines": [
                        [layout_type,".label(text="] + text_input + icon + [")"]
                    ],
                    "indented": []
                }
            ],
            "errors": error_list
        }

    def needed_imports(self):
        return ["bpy"]