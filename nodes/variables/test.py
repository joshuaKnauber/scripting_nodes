import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_BooleanNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_BooleanNode"
    bl_label = "Boolean"
    bl_icon = "MONKEY"
    node_color = (0,1,1)

    def inititialize(self, context):
        self.sockets.create_output(self,"BOOL","bool",False)

    def evaluate(self, socket, input_data):
        blocks = [
                    {
                        "lines": [
                            
                        ],
                        "indented": [
                            
                        ]
                    }
                ]

        errors = []

        return {"blocks": blocks, "errors": errors}