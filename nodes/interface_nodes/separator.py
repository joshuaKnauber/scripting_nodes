import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons


class SN_UiSeparatorNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node to create a separator in the user interface'''
    bl_idname = 'SN_UiSeparatorNode'
    bl_label = "Separator"
    bl_icon = node_icons["INTERFACE"]

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.inputs.new('SN_LayoutSocket', "Layout")

        self.outputs.new('SN_LayoutSocket', "Layout")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        pass# draws extra buttons on node

    def evaluate(self, output):
        errors = []

        return {"code":["_INDENT__INDENT_",self.outputs[0].links[0].to_node.layout_type(),
                        ".separator()"], "error":errors}