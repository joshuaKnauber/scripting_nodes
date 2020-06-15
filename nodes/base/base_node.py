import bpy
from ...compile.compiler import compiler
from...handler.error_handling import ErrorHandler


class SN_ScriptingBaseNode:
    bl_width_min = 40
    bl_width_default = 160
    bl_width_max = 5000

    _should_be_registered = False

    ErrorHandler = ErrorHandler()

    def socket_update(self, context):
        compiler().socket_update(context)

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'SN_ScriptingNodesTree'

    def update(self):
        pass
    
    def evaluate(self, output):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines

                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines

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

    def layout_type(self):
        return ""

    def get_register_block(self):
        return ["pass"]

    def get_unregister_block(self):
        return ["pass"]

    def needed_imports(self):
        return ["bpy"]