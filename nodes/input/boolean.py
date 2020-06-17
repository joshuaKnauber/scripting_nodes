import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_BooleanNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BooleanNode"
    bl_label = "Boolean"
    bl_icon = node_icons["INPUT"]
    _should_be_registered = False

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    value: bpy.props.BoolProperty(
        name="Value",
        description="Output Value",
        default=False,
        update=socket_update
    )

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INPUT"]

        self.outputs.new("SN_BooleanSocket", "Output")

    def draw_buttons(self, context, layout):
        layout.prop(self,"value",text=str(self.value), toggle=True)

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