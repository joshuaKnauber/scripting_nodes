#SN_ScriptLineNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_ScriptLineNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ScriptLineNode"
    bl_label = "Script Line"
    bl_icon = "FILE_SCRIPT"
    node_color = (1,1,1)
    should_be_registered = False

    line: bpy.props.StringProperty(name="Line", description="The line you want to write")

    def inititialize(self,context):
        self.sockets.create_input(self,"EXECUTE","Execute")
        self.sockets.create_output(self,"EXECUTE","Execute")

    def draw_buttons(self, context, layout):
        layout.prop(self, "line", text="")

    def evaluate(self, socket, input_data, errors):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": []
        }
