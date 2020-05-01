import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ..node_utility import register_dynamic_input, get_input_value
from ...node_sockets import update_socket_autocompile


# https://docs.blender.org/api/current/bpy.types.Panel.html

# bl_category
# bl_context
# bl_options
# bl_order
# bl_region_type
# bl_space_type

# draw_header(context):
#    draw a header for the panel
# draw_header_preset(context):
#    draw elements for presets for the header


class SN_UiPanelNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node to create a panel in the user interface'''
    bl_idname = 'SN_UiPanelNode'
    bl_label = "Panel"
    bl_icon = node_icons["INTERFACE"]

    panel_name: bpy.props.StringProperty(default="New Panel",name="Panel name",description="Name of the panel", update=update_socket_autocompile)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.inputs.new('SN_LayoutSocket', "Layout")
        self.inputs.new('SN_BooleanSocket', "Should display")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self,"panel_name",text="Name")

    def layout_type(self):
        return "layout"

    def evaluate(self,output):
        errors = []
        pollValue, error = get_input_value(self, "Should display", "SN_BooleanSocket")
        errors+=error
        idname = "SN_PT_" + self.panel_name.title().replace(" ","")
        header = ["class " + idname + "(bpy.types.Panel):\n",
                "_INDENT_bl_label = '"+self.panel_name+"'\n",
                "_INDENT_bl_idname = '" + idname + "'\n",
                "_INDENT_bl_space_type = 'PROPERTIES'\n",
                "_INDENT_bl_region_type = 'WINDOW'\n",
                "_INDENT_bl_context = 'scene'\n\n",
                "_INDENT_@classmethod\n",
                "_INDENT_def poll(self, context):\n",
                "_INDENT__INDENT_return ", pollValue ,"\n\n",
                "_INDENT_def draw(self, context):\n",
                "_INDENT__INDENT_layout = self.layout\n"]

        code = []
        for inp in self.inputs:
            if inp.bl_idname == "SN_LayoutSocket" and inp.is_linked:
                if inp.bl_idname == "SN_LayoutSocket":
                    code += [inp.links[0].from_socket,"\n"]
                else:
                    errors.append("wrong_socket")
        
        return {"code":header+code,"error":errors}

    def update(self):
        register_dynamic_input(self, "SN_LayoutSocket", "Layout")