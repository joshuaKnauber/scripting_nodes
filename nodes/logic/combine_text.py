import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_CombineText(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CombineText"
    bl_label = "Combine Text"
    bl_icon = node_icons["LOGIC"]
    _should_be_registered = False

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["LOGIC"]
        self.outputs.new("SN_StringSocket", "OUTPUT")
        self.inputs.new("SN_StringSocket", "INPUT")
        self.inputs.new("SN_StringSocket", "INPUT")

    def evaluate(self, output):
        value1, errors = self.SocketHandler.socket_value(self.inputs[0])
        value2, error = self.SocketHandler.socket_value(self.inputs[1])
        errors+=error

        return {
            "blocks": [
                {
                    "lines": [
                        value1 + [" + "] + value2
                    ],
                    "indented": [
                        
                    ]
                }
            ],
            "errors": [
            ]
        }

    def needed_imports(self):
        return []