import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_NumberNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_NumberNode"
    bl_label = "Number"
    bl_icon = node_icons["INPUT"]
    _should_be_registered = False

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    value: bpy.props.FloatProperty(
        name="Value",
        description="Output Value",
        default=0,
        update=socket_update
    )

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INPUT"]

        self.outputs.new("SN_FloatSocket", "Output")

    def draw_buttons(self, context, layout):
        layout.prop(self,"value")

    def evaluate(self, output):
        return {
            "blocks": [
                {
                    "lines": [
                        [str(self.value)]
                    ],
                    "indented": [
                        
                    ]
                }
            ],
            "errors": []
        }

    def needed_imports(self):
        return []