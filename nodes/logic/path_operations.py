#SN_PathOperationsNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_PathOperationsNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PathOperationsNode"
    bl_label = "Path Operations"
    bl_icon = "PARTICLE_DATA"
    node_color = (0.125,0.125,0.125)
    should_be_registered = False

    docs = {
        "text": ["This node is used to do <important>operations on a path</>.",
                ""],
        "python": ["os.path.dirname(<string>filepath</>)"]

    }

    operation: bpy.props.EnumProperty(items=[("dirname", "Directory", "The path to the directory your file is in"), ("basename", "Basename", "The final component of a path")], name="Operation")

    def inititialize(self,context):
        self.sockets.create_input(self,"STRING","Path")
        self.sockets.create_output(self,"STRING","Output")
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "operation", expand=True)

    def evaluate(self, socket, node_data, errors):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        ["os.path." + self.operation +"(", node_data["input_data"][0]["code"], ")"]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }

    def required_imports(self):
        return ["os"]

