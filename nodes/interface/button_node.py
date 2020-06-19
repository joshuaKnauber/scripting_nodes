import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons
from random import randint


class SN_Button(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_Button"
    bl_label = "Button"
    bl_width_default = 300
    bl_icon = node_icons["INTERFACE"]

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.inputs.new("SN_StringSocket", "Text").value = "New Button"

        self.outputs.new("SN_LayoutSocket", "Layout")

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

    operator: bpy.props.StringProperty(name="Operator",description="The operator for the given button",update=update_operator)

    def draw_buttons(self, context, layout):
        self.draw_icon_chooser(layout)
        layout.prop_search(self, "operator", context.scene, "sn_operators", text="")

    def evaluate(self, output):
        error_list = []

        layout_type, errors = self.SocketHandler.get_layout_type(self.outputs[0])
        error_list += errors

        text_input, errors = self.SocketHandler.socket_value(self.inputs[0])
        error_list += errors

        icon = []
        if self.icon:
            icon = [",icon=\""+self.icon+"\""]

        return {
            "blocks": [
                {
                    "lines": [
                        [layout_type,".label(text="] + text_input + icon + [")"]
                    ],
                    "indented": []
                }
            ],
            "errors": error_list
        }

    def needed_imports(self):
        return ["bpy"]