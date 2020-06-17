import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_DataToString(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DataToString"
    bl_label = "Data to String"
    bl_icon = node_icons["LOGIC"]
    _should_be_registered = False

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["LOGIC"]

        self.inputs.new('SN_DataSocket', "Data")
        self.outputs.new("SN_StringSocket", "Output")

    def draw_buttons(self, context, layout):
        pass

    def evaluate(self, output):
        value, errors = self.SocketHandler.socket_value(self.inputs[0])

        return {
            "blocks": [
                {
                    "lines": [
                        ["str("] + value + [")"]
                    ],
                    "indented": [
                    ]
                }
            ],
            "errors": [
            ]
        }

    def needed_imports(self):
        return []