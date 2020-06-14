import bpy
from ..base.base_node import SN_ScriptingBaseNode


import bpy


class SN_IfProgramNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IfProgramNode"
    bl_label = "If (Program)"
    _should_be_registered = True

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def init(self, context):
        self.inputs.new("SN_ProgramSocket", "program")
        self.outputs.new("SN_ProgramSocket", "continue")
        self.outputs.new("SN_ProgramSocket", "do")
        self.outputs.new("SN_ProgramSocket", "else")
    
    def evaluate(self, output):
        return {
            "blocks": [
                {
                    "lines": [
                        ["if True:"]
                    ],
                    "indented": [
                        ["pass"]
                    ]
                },
                {
                    "lines": [
                        ["else:"]
                    ],
                    "indented": [
                        ["pass"]
                    ]
                }
            ],
            "errors": [
                {
                    "error": "",
                    "node": self,
                    "socket": None
                }
            ]
        }

    def get_register_block(self):
        return ["pass"]

    def get_unregister_block(self):
        return ["pass"]

    def needed_imports(self):
        return ["bpy"]