import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_IfNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IfNode"
    bl_label = "If (Program)"
    bl_icon = node_icons["PROGRAM"]
    _should_be_registered = False

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["PROGRAM"]
        
        inp = self.inputs.new('SN_ProgramSocket', "Program")
        inp.display_shape = "DIAMOND"

        self.inputs.new('SN_BooleanSocket', "Value")

        out = self.outputs.new('SN_ProgramSocket', "Program")
        out.display_shape = "DIAMOND"

        out = self.outputs.new('SN_ProgramSocket', "Do")
        out.display_shape = "DIAMOND"

        out = self.outputs.new('SN_ProgramSocket', "Else")
        out.display_shape = "DIAMOND"

    def evaluate(self, output):
        continue_code, errors = self.SocketHandler.socket_value(self.outputs[0])
        value, error = self.SocketHandler.socket_value(self.inputs[1])
        errors+=error
        do_code, error = self.SocketHandler.socket_value(self.outputs[1])
        errors+=error
        else_code, error = self.SocketHandler.socket_value(self.outputs[2])
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