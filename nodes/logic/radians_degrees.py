#SN_RadiansNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_RadiansNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RadiansNode"
    bl_label = "Radians - Degrees"
    bl_icon = "MESH_CIRCLE"
    bl_width_default = 230
    node_color = (0.125,0.125,0.125)
    should_be_registered = False

    docs = {
        "text": ["This node is used to <important>convert radians into degrees and vice versa</>."
                ""],
        "python": ["<number>8</> * <number>4</>"]

    }

    operation: bpy.props.EnumProperty(items=[("degrees", "Radians to Degrees", "Convert Radians to Degrees"), ("radians", "Degrees to Radians", "Convert Degrees to radians")],name="Operation")

    def inititialize(self,context):
        self.sockets.create_input(self,"FLOAT","Input")
        self.sockets.create_output(self,"FLOAT","Output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "operation", expand=True)

    def evaluate(self, socket, node_data, errors):
        return {
            "blocks": [
                {
                    "lines": [
                        ["math.", self.operation, "(", node_data["input_data"][0]["code"], ")"]
                    ],
                    "indented": [
                    ]
                }
            ],
            "errors": errors
        }

    def required_imports(self):
        return ["bpy", "math"]