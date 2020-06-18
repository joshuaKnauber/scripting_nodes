import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons
from random import randint


class SN_Box(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_Box"
    bl_label = "Box"
    bl_icon = node_icons["INTERFACE"]

    _dynamic_layout_sockets = True

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.inputs.new("SN_BooleanSocket", "Enabled").value = True
        self.inputs.new("SN_BooleanSocket", "Alert").value = False

        self.inputs.new("SN_FloatSocket", "Scale X").value = 1
        self.inputs.new("SN_FloatSocket", "Scale Y").value = 1
        
        self.outputs.new("SN_LayoutSocket", "Layout")

    def draw_buttons(self, context, layout):
        pass

    def evaluate(self, output):
        error_list = []

        layout_type, errors = self.SocketHandler.get_layout_type(self.outputs[0])
        error_list += errors

        enabled, errors = self.SocketHandler.socket_value(self.inputs["Enabled"])
        error_list += errors
        
        alert, errors = self.SocketHandler.socket_value(self.inputs["Alert"])
        error_list += errors
        
        scale_x, errors = self.SocketHandler.socket_value(self.inputs["Scale X"])
        error_list += errors
        
        scale_y, errors = self.SocketHandler.socket_value(self.inputs["Scale Y"])
        error_list += errors

        layouts = []
        for input_socket in self.inputs:
            if input_socket.bl_idname == "SN_LayoutSocket":
                if input_socket.is_linked:
                    layouts.append(input_socket.links[0].from_socket)

        return {
            "blocks": [
                {
                    "lines": [
                        ["box = ",layout_type,".box()"],
                        ["box.enabled = "] + enabled,
                        ["box.alert = "] + alert,
                        ["box.scale_x = "] + scale_x,
                        ["box.scale_y = "] + scale_y
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
        return "box"

    def needed_imports(self):
        return ["bpy"]