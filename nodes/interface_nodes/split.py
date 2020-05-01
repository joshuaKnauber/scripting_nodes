import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ..node_utility import register_dynamic_input


class SN_UiSplitNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node to create a split in the user interface'''
    bl_idname = 'SN_UiSplitNode'
    bl_label = "Split"
    bl_icon = node_icons["INTERFACE"]

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        inp = self.inputs.new('SN_FactorSocket', "Factor [0-1]")
        inp.value = 0.5

        self.inputs.new('SN_LayoutSocket', "Layout")
        self.inputs.new('SN_LayoutSocket', "Layout")

        self.outputs.new('SN_LayoutSocket', "Layout")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        pass# draws extra buttons on node

    def layout_type(self):
        return "split"

    def evaluate(self, output):
        errors = []

        factor = str(self.inputs[0].value)
        if self.inputs[0].is_linked:
            if self.inputs[0].links[0].from_socket.bl_idname == "SN_NumberSocket":
                factor = self.inputs[0].links[0].from_socket
            else:
                errors.append("wrong_socket")

        header = ["_INDENT__INDENT_split = ",self.outputs[0].links[0].to_node.layout_type(),".split(factor=",factor,")\n"]

        code = []
        for inp in self.inputs:
            if inp.bl_idname == "SN_LayoutSocket" and inp.is_linked:
                if inp.links[0].from_socket.bl_idname == "SN_LayoutSocket":
                    code += [inp.links[0].from_socket,"\n"]
                else:
                    errors.append("wrong_socket")

        return {"code":header+code,"error":errors}