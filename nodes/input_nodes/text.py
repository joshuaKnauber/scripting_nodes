import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons


class SN_TextNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Text Node for outputing Text'''
    bl_idname = 'SN_TextNode'
    bl_label = "Text"
    bl_icon = node_icons["INPUT"]

    text: bpy.props.StringProperty(
        name="Text",
        description="Text Input"
    )

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INPUT"]

        self.outputs.new('SN_StringSocket', "")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self, "text", text="")

    def evaluate(self, output):
        return {"code": ["'",self.text,"'"]}
        
        