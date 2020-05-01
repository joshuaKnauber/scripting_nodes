import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons



class SN_UiLabelNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node to create a label in the user interface'''
    bl_idname = 'SN_UiLabelNode'
    bl_label = "Label"
    bl_icon = node_icons["INTERFACE"]

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.inputs.new('SN_StringSocket', "Text")

        self.outputs.new('SN_LayoutSocket', "Layout")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        pass# draws extra buttons on node

    def evaluate(self, output):
        value = "'" + self.inputs[0].value + "'"
        errors = []

        if self.inputs[0].is_linked:
            if self.inputs[0].links[0].from_socket.bl_idname == "SN_StringSocket":
                value = self.inputs[0].links[0].from_socket
            else:
                errors.append("wrong_socket")

        return {"code":["_INDENT__INDENT_",self.outputs[0].links[0].to_node.layout_type(),
                        ".label(text=",value,")"], "error":errors}