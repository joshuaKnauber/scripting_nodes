import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons

class SN_NumberNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Outputs a number'''
    bl_idname = 'SN_NumberNode'
    bl_label = "Number"
    bl_icon = node_icons["INPUT"]  

    number: bpy.props.FloatProperty(
        name="Number",
        description="Value",
        default=0
    )

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INPUT"] 

        self.outputs.new('SN_NumberSocket', "")

    
    def draw_buttons(self, context, layout):
        layout.prop(self,"number",text="")

    def evaluate(self, output):
        if str(type(self.outputs[0].links[0].to_socket)) == "<class 'blender_visual_scripting_addon.node_sockets.SN_NumberSocket'>":
            return {"code": [str(self.number)]}
        else:
            return {"code": ["0"], "error": ["wrong_socket"]}
        