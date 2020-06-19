import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ..base.node_looks import node_colors, node_icons

class SN_PrintNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PrintNode"
    bl_label = "Print"
    bl_icon = node_icons["PROGRAM"]
    _should_be_registered = False

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["PROGRAM"]

        self.inputs.new("SN_ProgramSocket", "Program").display_shape = "DIAMOND"
        self.inputs.new("SN_DataSocket", "Value")
        self.outputs.new("SN_ProgramSocket", "Program").display_shape = "DIAMOND"
    
    def evaluate(self, output):
        value, errors = self.SocketHandler.socket_value(self.inputs[1])
        continue_code, error = self.SocketHandler.socket_value(self.outputs[0], False)
        errors+=error
        return {
            "blocks": [
                {
                    "lines": [
                        ["print("] + value + [")"]
                    ],
                    "indented": [
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