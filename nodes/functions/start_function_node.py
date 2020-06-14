import bpy
from ..base.base_node import SN_ScriptingBaseNode


class SN_StartFunction(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_StartFunction"
    bl_label = "Start Function"
    _should_be_registered = True

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def init(self, context):
        self.outputs.new("SN_ProgramSocket", "program")
    
    def evaluate(self, output):
        function_code = ["pass"]
        if self.outputs[0].is_linked:
            function_code = self.outputs[0].links[0].to_socket
        return {
            "blocks": [
                {
                    "lines": [
                        ["def test():"]
                    ],
                    "indented": [
                        function_code
                    ]
                }
            ],
            "errors": [
            ]
        }

    def get_register_block(self):
        return []

    def get_unregister_block(self):
        return []

    def needed_imports(self):
        return []