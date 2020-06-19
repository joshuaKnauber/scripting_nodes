import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons
from random import randint


class SN_RunOperator(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RunOperator"
    bl_label = "Run Operator"
    bl_width_default = 300
    bl_icon = node_icons["OPERATOR"]


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

        self.inputs.new("SN_ProgramSocket", "Program").display_shape = "DIAMOND"
        self.outputs.new("SN_ProgramSocket", "Program").display_shape = "DIAMOND"

    def get_socket_items(self, socket):
        """ returns the enum items for the given socket """
        return self.OperatorHandler.get_enum_items(self.operator, socket.name)

    def update_operator(self, context):
        """ update function for the operator type """
        properties = self.OperatorHandler.get_operator_properties(self.operator)
        for input_socket in self.inputs:
            if not input_socket == self.inputs[0]:
                self.inputs.remove(input_socket)
        for op_prop in properties:
            self.inputs.new(op_prop[1],op_prop[0])

    operator: bpy.props.StringProperty(name="Operator",description="The operator you want to run",update=update_operator)

    def draw_buttons(self, context, layout):
        layout.prop_search(self, "operator", context.scene, "sn_operators", text="")

    def evaluate(self, output):
        error_list = []

        continue_code, errors = self.SocketHandler.socket_value(self.outputs[0])
        error_list += errors

        op_props = []
        for input_socket in self.inputs:
            if not input_socket == self.inputs[0]:
                socket_value, errors = self.SocketHandler.socket_value(input_socket)
                error_list += errors
                op_props+=[self.OperatorHandler.get_property_identifier(self.operator,input_socket.name),"="] + socket_value + [", "]

        identifier = self.OperatorHandler.get_ops_string(self.operator)

        return {
            "blocks": [
                {
                    "lines": [
                        [identifier + "("] + op_props + [")"]
                    ],
                    "indented": []
                },
                {
                    "lines": [
                        continue_code
                    ],
                    "indented": [
                    ]
                }
            ],
            "errors": error_list
        }

    def needed_imports(self):
        return ["bpy"]