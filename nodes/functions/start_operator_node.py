import bpy
from ..base.base_node import SN_ScriptingBaseNode


class SN_StartOperator(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_StartOperator"
    bl_label = "Start Operator"
    _should_be_registered = True

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def init(self, context):
        self.outputs.new("SN_ProgramSocket", "execute")
    
    def evaluate(self, output):
        execute_code = ["pass"]
        if self.outputs[0].is_linked:
            execute_code = self.outputs[0].links[0].to_socket
        return {
            "blocks": [
                {
                    "lines": [
                        ["class SN_OT_TestOperator(bpy.types.Operator):"]
                    ],
                    "indented": [
                        ["bl_idname = \"my_operator.my_class_name\""],
                        ["bl_label = \"My Class Name\""],
                        ["bl_description = \"Description that shows in blender tooltips\""],
                        ["bl_options = {\"REGISTER\"}"],
                        [""],
                        {
                            "lines": [
                                ["@classmethod"],
                                ["def poll(cls, context):"]
                            ],
                            "indented": [
                                ["return True"]
                            ]
                        },
                        [""],
                        {
                            "lines": [
                                ["def execute(self, context):"]
                            ],
                            "indented": [
                                execute_code,
                                ["return {\"FINISHED\"}"]
                            ]
                        }
                    ]
                }
            ],
            "errors": [
            ]
        }

    def get_register_block(self):
        return ["bpy.utils.register_class(SN_OT_TestOperator)"]

    def get_unregister_block(self):
        return ["bpy.utils.unregister_class(SN_OT_TestOperator)"]

    def needed_imports(self):
        return ["bpy"]