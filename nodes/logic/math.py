import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_MathNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_MathNode"
    bl_label = "Math"
    bl_icon = node_icons["LOGIC"]
    _should_be_registered = False

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    operation: bpy.props.EnumProperty(
        items=[("+", "Add", "Add numbers"), ("-", "Subtract", "Subtract numbers"),
                ("*", "Multiply", "Multiply Numbers"), ("/", "Divide", "Divide Numbers")],
        name="Operation",
        description="Math operation for this node",
        update = socket_update
    )

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["LOGIC"]

        self.inputs.new('SN_FloatSocket', "Value")
        self.inputs.new('SN_FloatSocket', "Value")
        self.outputs.new('SN_FloatSocket', "Value")

    def draw_buttons(self, context, layout):
        layout.prop(self,"operation",text="")

    def evaluate(self, output):
        value1, errors = self.SocketHandler.socket_value(self.inputs[0])
        value2, error = self.SocketHandler.socket_value(self.inputs[1])
        errors+=error

        return {
            "blocks": [
                {
                    "lines": [
                        ["("] + value1 + [" " + self.operation + " "] + value2 + [")"]
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