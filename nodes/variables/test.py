import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_BooleanNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BooleanNode"
    bl_label = "Boolean"
    bl_icon = "MONKEY"
    node_color = (0,1,1)

    def inititialize(self, context):
        self.sockets.create_input("STRING","test",False)
        self.sockets.create_output("STRING","test",False)

    def evaluate(self, socket, input_data):
        return {
            "blocks": [
                {
                    "lines": [
                        
                    ],
                    "indented": [
                        
                    ]
                }
            ],
            "errors": []
        }

    def required_imports(self):
        return []