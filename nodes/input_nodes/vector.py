import bpy
from ...node_sockets import update_socket_autocompile
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons

class SN_VectorNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Outputs a float vector'''
    bl_idname = 'SN_VectorNode'
    bl_label = "Vector"
    bl_icon = node_icons["INPUT"]

    value: bpy.props.FloatVectorProperty(
        name="Vector",
        description="Values",
        default=(0, 0, 0),
        update=update_socket_autocompile
    )

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INPUT"]

        self.outputs.new('SN_VectorSocket', "")

    
    def draw_buttons(self, context, layout):
        col = layout.column()
        col.prop(self,"value",text="")

    def evaluate(self, output):
        return {"code": ["("+str(self.value[0])+","+str(self.value[1])+","+str(self.value[2])+")"]}
        