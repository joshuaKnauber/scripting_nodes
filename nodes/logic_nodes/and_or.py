import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons

class SN_AndOrNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node for and or comparison'''
    bl_idname = 'SN_AndOrNode'
    bl_label = "And/Or"
    bl_icon = node_icons["LOGIC"]

    operation: bpy.props.EnumProperty(
        items=[("and", "and", "Both values need to be True"), ("or", "or", "Only one value needs to be True")],
        name="Operation",
        description="Operation for this node"
    )

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["LOGIC"]

        self.inputs.new('SN_BooleanSocket', "Value")
        self.inputs.new('SN_BooleanSocket', "Value")
        self.outputs.new('SN_BooleanSocket', "Output")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass

    def draw_buttons(self, context, layout):
        layout.prop(self,"operation",text="")

    def evaluate(self,output):
        value1 = str(self.inputs[0].value)
        value2 = str(self.inputs[1].value)

        if self.inputs[0].is_linked:
            value1 = self.inputs[0].links[0].from_socket
        if self.inputs[1].is_linked:
            value2 = self.inputs[1].links[0].from_socket

        if str(type(self.outputs[0].links[0].to_socket)) == "<class 'blender_visual_scripting_addon.node_sockets.SN_BooleanSocket'>":
            return {"code": [value1, " ", self.operation, " ", value2]}
        else:
            return {"code": ["0"], "error": ["wrong_socket"]}
