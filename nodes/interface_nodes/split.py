import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ..node_utility import register_dynamic_input, get_input_value


class SN_UiSplitNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node to create a split in the user interface'''
    bl_idname = 'SN_UiSplitNode'
    bl_label = "Split"
    bl_icon = node_icons["INTERFACE"]

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        inp = self.inputs.new('SN_FactorSocket', "Factor")
        inp.value = 0.5

        self.inputs.new('SN_BooleanSocket', "Align")
        self.inputs.new('SN_BooleanSocket', "Enabled").value = True
        self.inputs.new('SN_BooleanSocket', "Alert")
        self.inputs.new('SN_NumberSocket', "Scale X").value = 1
        self.inputs.new('SN_NumberSocket', "Scale Y").value = 1

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

        align, error = get_input_value(self,"Align","SN_BooleanSocket")
        errors += error

        enabled, error = get_input_value(self,"Enabled","SN_BooleanSocket")
        errors += error

        alert, error = get_input_value(self,"Alert","SN_BooleanSocket")
        errors += error

        scale_x, error = get_input_value(self,"Scale X","SN_BooleanSocket")
        errors += error

        scale_y, error = get_input_value(self,"Scale Y","SN_NumberSocket")
        errors += error

        header = ["_INDENT__INDENT_split = ",self.outputs[0].links[0].to_node.layout_type(),".split(factor=",factor,",align=",align,")\n"]
        header += ["_INDENT__INDENT_split.enabled = ",enabled,"\n"]
        header += ["_INDENT__INDENT_split.alert = ",alert,"\n"]
        header += ["_INDENT__INDENT_row.scale_x = ",scale_x,"\n"]
        header += ["_INDENT__INDENT_row.scale_y = ",scale_y,"\n"]

        code = []
        for inp in self.inputs:
            if inp.bl_idname == "SN_LayoutSocket" and inp.is_linked:
                if inp.links[0].from_socket.bl_idname == "SN_LayoutSocket":
                    code += [inp.links[0].from_socket,"\n"]
                else:
                    errors.append("wrong_socket")

        return {"code":header+code,"error":errors}