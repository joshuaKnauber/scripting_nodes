import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ..node_utility import register_dynamic_input


class SN_UiPanelNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node to create a panel in the user interface'''
    bl_idname = 'SN_UiPanelNode'
    bl_label = "Panel"
    bl_icon = node_icons["INTERFACE"]

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.inputs.new('SN_LayoutSocket', "Layout")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        pass# draws extra buttons on node

    def evaluate(self,output):
        code = ["'panel code'\n"]
        for inp in self.inputs:
            if inp.bl_idname == "SN_LayoutSocket" and inp.is_linked:
                code += ["layout.",inp.links[0].from_socket,"\n"]
        
        return {"code":code}

    def update(self):
        register_dynamic_input(self, "SN_LayoutSocket", "Layout")