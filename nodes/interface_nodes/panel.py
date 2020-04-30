import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ..node_utility import register_dynamic_input


class SN_UiPanelNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node to create a panel in the user interface'''
    bl_idname = 'SN_UiPanelNode'
    bl_label = "Panel"
    bl_icon = node_icons["INTERFACE"]

    panel_name: bpy.props.StringProperty(default="New Panel",name="Panel name",description="Name of the panel")

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.inputs.new('SN_LayoutSocket', "Layout")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self,"panel_name",text="Name")

    def layout_type(self):
        return "layout"

    def evaluate(self,output):
        header = ["class LayoutDemoPanel(bpy.types.Panel):\n",
                "_INDENT_bl_label = '"+self.panel_name+"'\n",
                "_INDENT_bl_idname = 'SN_PT_"+self.panel_name.title().replace(" ","")+"'\n",
                "_INDENT_bl_space_type = 'PROPERTIES'\n",
                "_INDENT_bl_region_type = 'WINDOW'\n",
                "_INDENT_bl_context = 'scene'\n\n",
                "_INDENT_def draw(self, context):\n"]

        code = []
        for inp in self.inputs:
            if inp.bl_idname == "SN_LayoutSocket" and inp.is_linked:
                code += [inp.links[0].from_socket,"\n"]
        
        return {"code":header+code}

    def update(self):
        register_dynamic_input(self, "SN_LayoutSocket", "Layout")