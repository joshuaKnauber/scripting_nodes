import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ..node_utility import register_dynamic_input, get_input_value


class SN_UiBoxNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node to create a box in the user interface'''
    bl_idname = 'SN_UiBoxNode'
    bl_label = "Box Layout"
    bl_icon = node_icons["INTERFACE"]

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.inputs.new('SN_BooleanSocket', "Enabled").value = True
        self.inputs.new('SN_BooleanSocket', "Alert")

        self.outputs.new('SN_LayoutSocket', "Layout")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        pass# draws extra buttons on node

    def layout_type(self):
        return "box"

    def evaluate(self, output):

        errors = []

        enabled, error = get_input_value(self,"Enabled",["SN_BooleanSocket"])
        errors += error

        alert, error = get_input_value(self,"Alert",["SN_BooleanSocket"])
        errors += error

        header = ["_INDENT__INDENT_box = ",self.outputs[0].links[0].to_node.layout_type(),".box()\n"]
        header += ["_MATCH_PREV_box.enabled = ",enabled,"\n"]
        header += ["_MATCH_PREV_box.alert = ",alert,"\n"]

        code = []
        for inp in self.inputs:
            if inp.bl_idname == "SN_LayoutSocket" and inp.is_linked:
                if inp.links[0].from_socket.bl_idname == "SN_LayoutSocket":
                    code += [inp.links[0].from_socket]
                else:
                    errors.append("wrong_socket")

        return {"code":header+code,"error":errors}

    def update(self):
        register_dynamic_input(self, "SN_LayoutSocket", "Layout")