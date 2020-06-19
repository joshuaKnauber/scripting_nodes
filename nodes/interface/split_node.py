import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons
from random import randint


class SN_Split(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_Split"
    bl_label = "Split"
    bl_icon = node_icons["INTERFACE"]

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.inputs.new("SN_FloatSocket", "Factor").value = 0.5

        self.inputs.new("SN_BooleanSocket", "Aligned").value = False
        self.inputs.new("SN_BooleanSocket", "Enabled").value = True
        self.inputs.new("SN_BooleanSocket", "Alert").value = False

        self.inputs.new("SN_FloatSocket", "Scale X").value = 1
        self.inputs.new("SN_FloatSocket", "Scale Y").value = 1

        self.inputs.new("SN_LayoutSocket", "Layout")
        self.inputs.new("SN_LayoutSocket", "Layout")
        
        self.outputs.new("SN_LayoutSocket", "Layout")

    def draw_buttons(self, context, layout):
        pass

    def evaluate(self, output):
        error_list = []

        layout_type, errors = self.SocketHandler.get_layout_type(self.outputs[0])
        error_list += errors

        aligned, errors = self.SocketHandler.socket_value(self.inputs["Aligned"])
        error_list += errors
        
        enabled, errors = self.SocketHandler.socket_value(self.inputs["Enabled"])
        error_list += errors
        
        alert, errors = self.SocketHandler.socket_value(self.inputs["Alert"])
        error_list += errors
        
        scale_x, errors = self.SocketHandler.socket_value(self.inputs["Scale X"])
        error_list += errors
        
        scale_y, errors = self.SocketHandler.socket_value(self.inputs["Scale Y"])
        error_list += errors
        
        factor, errors = self.SocketHandler.socket_value(self.inputs["Factor"])
        error_list += errors

        layouts, errors = self.SocketHandler.get_layout_values(self)
        error_list += errors

        return {
            "blocks": [
                {
                    "lines": [
                        ["split = ",layout_type,".split(align="] + aligned + [",factor="] + factor + [")"],
                        ["split.enabled = "] + enabled,
                        ["split.alert = "] + alert,
                        ["split.scale_x = "] + scale_x,
                        ["split.scale_y = "] + scale_y
                    ],
                    "indented": []
                },
                {
                    "lines": layouts,
                    "indented": []
                }
            ],
            "errors": error_list
        }

    def layout_type(self):
        return "split"

    def needed_imports(self):
        return ["bpy"]