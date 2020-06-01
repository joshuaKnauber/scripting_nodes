import bpy
from ...node_sockets import update_socket_autocompile
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons

class SN_CombineTextNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node for combining two text inputs'''
    bl_idname = 'SN_CombineTextNode'
    bl_label = "Combine Text"
    bl_icon = node_icons["LOGIC"]

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["LOGIC"]

        self.inputs.new('SN_StringSocket', "INPUT")
        self.inputs.new('SN_StringSocket', "INPUT")
        self.outputs.new('SN_StringSocket', "Output")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass

    def draw_buttons(self, context, layout):
        pass

    def evaluate(self,output):
        value1 = "0"
        value2 = "0"

        errors = []

        if self.inputs[0].is_linked:
            if self.inputs[0].links[0].from_socket.bl_idname == "SN_StringSocket":
                value1 = self.inputs[0].links[0].from_socket
            else:
                errors.append("wrong_socket")
        else:
            value1 = "'" + self.inputs[0].value + "'"

        if self.inputs[1].is_linked:
            if self.inputs[1].links[0].from_socket.bl_idname == "SN_StringSocket":
                value2 = self.inputs[1].links[0].from_socket
            else:
                errors.append("wrong_socket")
        else:
            value2 = "'" + self.inputs[1].value + "'"

        return {"code": [value1," + ",value2],"error":errors}
