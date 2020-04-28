import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons

class SN_VectorNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Outputs a float vector'''
    bl_idname = 'SN_VectorNode'
    bl_label = "Vector"
    bl_icon = node_icons["INPUT"]

    vector: bpy.props.FloatVectorProperty(
        name="Vector",
        description="Values",
        default=(0, 0, 0)
    )

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INPUT"]

        self.outputs.new('SN_VectorSocket', "")

    
    def draw_buttons(self, context, layout):
        col=layout.column()
        col.prop(self,"vector",text="")

    def evaluate(self, output):
        if str(type(self.outputs[0].links[0].to_socket)) == "<class 'blender_visual_scripting_addon.node_sockets.SN_VectorSocket'>":
            return {"code": [str(self.vector[0]) + " ", str(self.vector[1]) + " ", str(self.vector[2])]}
        else:
            return {"code": ["(0, 0, 0)"], "error": ["wrong_socket"]}
        