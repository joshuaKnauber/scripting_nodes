import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_IfLayoutNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IfLayoutNode"
    bl_label = "If (Layout)"
    bl_icon = node_icons["INTERFACE"]
    _should_be_registered = False

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]
        
        self.inputs.new('SN_LayoutSocket', "Layout")
        self.inputs.new('SN_LayoutSocket', "Do")
        self.inputs.new('SN_LayoutSocket', "Else")

        self.inputs.new('SN_BooleanSocket', "Value")

        self.outputs.new('SN_LayoutSocket', "Layout")

    def layout_type(self):
        if self.outputs[0].is_linked:
            if self.outputs[0].links[0].to_socket.bl_idname == "SN_LayoutSocket":
                return self.outputs[0].links[0].to_node.layout_type()
        return "layout"

    def evaluate(self, output):
        continue_code, errors = self.SocketHandler.socket_value(self.inputs["Layout"],False)
        value, error = self.SocketHandler.socket_value(self.inputs["Value"])
        errors+=error
        do_code, error = self.SocketHandler.socket_value(self.inputs["Do"],False)
        errors+=error
        else_code, error = self.SocketHandler.socket_value(self.inputs["Else"],False)
        errors+=error
        if do_code == []:
            do_code = ["pass"]
        if else_code == []:
            else_code = ["pass"]

        return {
            "blocks": [
                {
                    "lines": [
                        ["if "] + value + [":"]
                    ],
                    "indented": [
                        do_code
                    ]
                }, 
                {
                    "lines": [
                        ["else:"]
                    ],
                    "indented": [
                        else_code
                    ]
                },
                {
                    "lines": [
                        continue_code
                    ],
                    "indented": [
                    ]
                }
            ],
            "errors": errors
        }


    def needed_imports(self):
        return []