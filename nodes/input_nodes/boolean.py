import bpy
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
        default=False
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
        if str(type(self.outputs[0].links[0].to_socket)) == "<class 'blender_visual_scripting_addon.node_sockets.SN_BooleanSocket'>":
            return {"code": [str(self.value)]}
        else:
            return {"code": ["False"], "error": ["wrong_socket"]}