import bpy
from ...node_sockets import update_socket_autocompile
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons


class SN_ScriptLineNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Script Line Node for outputing a script line'''
    bl_idname = 'SN_ScriptLineNode'
    bl_label = "Script Line"
    bl_icon = node_icons["OPERATOR"]

    text: bpy.props.StringProperty(
        name="Code",
        description="Text Input",
        update=update_socket_autocompile
    )

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

        self.inputs.new('SN_ProgramSocket', "")

        self.outputs.new('SN_ProgramSocket', "")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self, "text", text="")

    def evaluate(self, output):
        return {"code": [self.text,"\n"]}
        
        