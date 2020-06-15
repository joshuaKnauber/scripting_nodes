import bpy
from ..base.base_node import SN_ScriptingBaseNode


class SN_IfProgramNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IfProgramNode"
    bl_label = "If (Program)"
    _should_be_registered = False

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def init(self, context):
        self.inputs.new("SN_ProgramSocket", "program")
        self.outputs.new("SN_ProgramSocket", "continue")
        self.outputs.new("SN_ProgramSocket", "do")
        self.outputs.new("SN_ProgramSocket", "else")
    
    def evaluate(self, output):
        continue_code = ["pass"]
        if self.outputs[1].is_linked:
            continue_code = self.outputs[1].links[0].to_socket
        do_code = ["pass"]
        if self.outputs[2].is_linked:
            do_code = self.outputs[2].links[0].to_socket
        followup = []
        if self.outputs[0].is_linked:
            followup = self.outputs[0].links[0].to_socket
        return {
            "blocks": [
                {
                    "lines": [
                        ["if True:"]
                    ],
                    "indented": [
                        continue_code
                    ]
                },
                {
                    "lines": [
                        ["else:"]
                    ],
                    "indented": [
                        do_code
                    ]
                },
                {
                    "lines": [
                        followup
                    ],
                    "indented": []
                }
            ],
            "errors": [
            ]
        }

    def needed_imports(self):
        return []