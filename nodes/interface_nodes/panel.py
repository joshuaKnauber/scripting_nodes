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

    def evaluate(self,output):
        class LayoutDemoPanel(bpy.types.Panel):
            """Creates a Panel in the scene context of the properties editor"""
            bl_label = "Layout Demo"
            bl_idname = "SCENE_PT_layout"
            bl_space_type = 'PROPERTIES'
            bl_region_type = 'WINDOW'
            bl_context = "scene"

        header = ["bl_label = '"+self.panel_name+"'\n",
                "bl_idname = 'SN_PT_"+self.panel_name.title().replace(" ","")+"'\n",
                "bl_space_type = 'PROPERTIES'\n",
                "bl_region_type = 'WINDOW'\n",
                "bl_context = 'scene'\n\n"]

        code = []
        for inp in self.inputs:
            if inp.bl_idname == "SN_LayoutSocket" and inp.is_linked:
                code += ["layout.",inp.links[0].from_socket,"\n"]
        
        return {"code":["class LayoutDemoPanel(bpy.types.Panel):\n"],
                "indented_blocks":[
                    {
                        "code": header,
                        "function_node": None
                    },
                    {
                        "code": ["def draw(self, context):"]+code,
                        "function_node": None
                    }
                ]}

    def update(self):
        register_dynamic_input(self, "SN_LayoutSocket", "Layout")