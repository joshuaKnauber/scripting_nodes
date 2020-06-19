import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_ScriptLine(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ScriptLine"
    bl_label = "Script Line"
    bl_icon = node_icons["OPERATOR"]

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    line: bpy.props.StringProperty(name="Name", description="The name of the function", default="", update=socket_update)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]
        self.inputs.new("SN_ProgramSocket", "Program").display_shape = "DIAMOND"
        self.outputs.new("SN_ProgramSocket", "Program").display_shape = "DIAMOND"

    def draw_buttons(self, context, layout):
        layout.prop(self,"line")

    def evaluate(self, output):
        function_code, errors = self.SocketHandler.socket_value(self.outputs[0], False)

        return {
            "blocks": [
                {
                    "lines": [
                        [self.line]
                    ],
                    "indented": [
                    ]
                },
                {
                    "lines": [
                        function_code
                    ],
                    "indented": [
                    ]
                }
            ],
            "errors": errors
        }

    def needed_imports(self):
        return []