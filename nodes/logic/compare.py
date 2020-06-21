import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_CompareNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CompareNode"
    bl_label = "Compare"
    bl_icon = node_icons["LOGIC"]
    _should_be_registered = False

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def update_operation(self, context):
        if self.operation == "None":
            self.inputs.clear()
            inp = self.inputs.new('SN_SceneDataSocket', "Scene Data")
            inp.display_shape = "SQUARE"
        else:
            self.inputs.clear()
            self.inputs.new('SN_DataSocket', "Data")
            self.inputs.new('SN_DataSocket', "Data")

    operation: bpy.props.EnumProperty(
        items=[("==", "=", "Equal to"), ("!=", "≠", "Not equal to"),
                (">", ">", "Bigger than"), ("<", "<", "Smaller than"),
                (">=", "≥", "Bigger or equal to"), ("<=", "≤", "Smaller or equal to"),
                ("None", "Existing", "Check if Data exists")],
        name="Operation",
        description="Compare operation for this node",
        update = update_operation
    )

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["LOGIC"]
        self.inputs.new('SN_DataSocket', "Data")
        self.inputs.new('SN_DataSocket', "Data")
        self.outputs.new('SN_BooleanSocket', "Output")

    def draw_buttons(self, context, layout):
        layout.prop(self,"operation",text="")

    def evaluate(self, output):
        if self.operation != "None":
            value1, errors = self.SocketHandler.socket_value(self.inputs[0])
            value2, error = self.SocketHandler.socket_value(self.inputs[1])
            errors+=error

            return {
                "blocks": [
                    {
                        "lines": [
                            value1 + [" " + self.operation + " "] + value2
                        ],
                        "indented": [
                        ]
                    }
                ],
                "errors": [
                ]
            }
        else:
            value, errors = self.SocketHandler.socket_value(self.inputs[0])
            if not value:
                value = ["\" \""]

            return {
                "blocks": [
                    {
                        "lines": [
                            value + [" != None"]
                        ],
                        "indented": [
                        ]
                    }
                ],
                "errors": errors
            }

    def needed_imports(self):
        return []