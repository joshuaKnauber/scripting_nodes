import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ..node_utility import register_dynamic_input, get_input_value
from ...node_sockets import update_socket_autocompile


class SN_UiExistingPanelNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node to add to an existing panel in the user interface'''
    bl_idname = 'SN_UiExistingPanelNode'
    bl_label = "Append Panel"
    bl_icon = node_icons["INTERFACE"]
    bl_width_default = 200


    def get_panels(self):
        if len(bpy.context.scene.sn_panel_properties) == 0:
            for type_name in dir(bpy.types):
                type_class = eval("bpy.types." + type_name)
                if bpy.types.Panel in type_class.__bases__:

                    if type_class.bl_label != "":
                        item = bpy.context.scene.sn_panel_properties.add()
                        item.identifier = type_class.bl_rna.identifier
                        item.name = type_class.bl_label + " - " + type_class.bl_space_type.replace("_", " ").title()


    panel_name: bpy.props.StringProperty(name="Panel", description="The panel you want to edit", update=update_socket_autocompile)

    def init(self, context):
        self.get_panels()
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.inputs.new('SN_LayoutSocket', "Layout")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        update_socket_autocompile(self, context)

        layout.prop_search(self,"panel_name", context.scene,"sn_panel_properties",text="")

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
        errors = []
        code = []
        if self.panel_name != "":
            for item in bpy.context.scene.sn_panel_properties:
                if item.name == self.panel_name:
                    type_name = item.identifier
        else:
            errors.append("no_name")
            type_name = "test"


        header = ["_REMOVE_", "def append_panel_", type_name.replace(" ","_"), "(self, context):\n",
                  "_INDENT__INDENT_", "layout = self.layout \n"]

        for inp in self.inputs:
            if inp.bl_idname == "SN_LayoutSocket" and inp.is_linked:
                if inp.bl_idname == "SN_LayoutSocket":
                    code += [inp.links[0].from_socket]
                else:
                    errors.append("wrong_socket")

        if self.panel_name == "":
            header = [""]
            code = ["\n"]
        
        return {"code":header+code,"error":errors}

    def update(self):
        register_dynamic_input(self, "SN_LayoutSocket", "Layout")