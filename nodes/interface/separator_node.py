import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons
from random import randint


class SN_Separator(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_Separator"
    bl_label = "Separator"
    bl_icon = node_icons["INTERFACE"]

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.inputs.new("SN_FloatSocket", "Factor").value = 1
        
        self.outputs.new("SN_LayoutSocket", "Layout")

    def draw_buttons(self, context, layout):
        pass

    def evaluate(self, output):
        error_list = []

        layout_type, errors = self.SocketHandler.get_layout_type(self.outputs[0])
        error_list += errors

        factor, errors = self.SocketHandler.socket_value(self.inputs["Factor"])
        error_list += errors

        return {
            "blocks": [
                {
                    "lines": [
                        [layout_type,".separator(factor="] + factor + [")"],
                    ],
                    "indented": []
                }
            ],
            "errors": error_list
        }

    def needed_imports(self):
        return ["bpy"]