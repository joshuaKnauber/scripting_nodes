import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ..node_utility import register_dynamic_input, get_input_value
from ...node_sockets import update_socket_autocompile

# bpy.types .__bases__
# if bpy.types.panel is in that
# isPanel = True

class SN_UiExistingPanelNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node to add to an existing panel in the user interface'''
    bl_idname = 'SN_UiExistingPanelNode'
    bl_label = "Add to Panel"
    bl_icon = node_icons["INTERFACE"]
    bl_width_default = 200

    def get_panels():
        panels = []

        for type_name in dir(bpy.types):
            type_class = eval("bpy.types." + type_name)
            if bpy.types.Panel in type_class.__bases__:
                panels.append((type_class.bl_rna.identifier, type_class.bl_label, ""))
        return panels

    panel_name: bpy.props.EnumProperty(items=get_panels(), name="Panel", description="The panel you want to edit", update=update_socket_autocompile)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.inputs.new('SN_LayoutSocket', "Layout")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self,"panel_name")

    def layout_type(self):
        return "layout"

    def options(self):
        if not self.default_closed and not self.hide_header:
            return ""
        options = "_INDENT_bl_options = {"
        if self.default_closed:
            options+="'DEFAULT_CLOSED', "
        if self.hide_header:
            options+="'HIDE_HEADER'"
        options+="}\n"
        return options

    def evaluate(self,output):
        type_name = self.panel_name

        header = ["_REMOVE_", "def append_panel_", type_name.replace(" ","_"), "(self, context):\n"]

        errors = []
        code = []
        for inp in self.inputs:
            if inp.bl_idname == "SN_LayoutSocket" and inp.is_linked:
                if inp.bl_idname == "SN_LayoutSocket":
                    code += [inp.links[0].from_socket]
                else:
                    errors.append("wrong_socket")
        
        return {"code":header+code,"error":errors}

    def update(self):
        register_dynamic_input(self, "SN_LayoutSocket", "Layout")