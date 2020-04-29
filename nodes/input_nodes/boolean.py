import bpy
from ...node_sockets import update_socket_autocompile
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons


class SN_BoolNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Input Node for boolean'''
    bl_idname = 'SN_BoolNode'
    bl_label = "Boolean"
    bl_icon = node_icons["INPUT"] 

    value: bpy.props.BoolProperty(
        name="Value",
        description="Output Value",
        default=False,
        update=update_socket_autocompile
    )

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INPUT"]

        self.outputs.new('SN_BooleanSocket', "")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self,"value",text=str(self.value), toggle=True)

    def evaluate(self, output):
        return {"code": [str(self.value)]}