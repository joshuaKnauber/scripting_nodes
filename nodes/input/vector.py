import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_VectorNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_VectorNode"
    bl_label = "Vector"
    bl_icon = node_icons["INPUT"]
    _should_be_registered = False

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    value: bpy.props.FloatVectorProperty(
        name="Vector",
        description="Values",
        default=(0, 0, 0),
        update=socket_update
    )

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INPUT"]

        self.outputs.new("SN_VectorSocket", "Output")

    def draw_buttons(self, context, layout):
        col = layout.column()
        col.prop(self,"value")

    def evaluate(self, output):
        return {
            "blocks": [
                {
                    "lines": [
                        ["("+str(self.value[0])+","+str(self.value[1])+","+str(self.value[2])+")"]
                    ],
                    "indented": [
                        
                    ]
                }
            ],
            "errors": []
        }

    def needed_imports(self):
        return []