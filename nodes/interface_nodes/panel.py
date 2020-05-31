import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ..node_utility import register_dynamic_input, get_input_value
from ...node_sockets import update_socket_autocompile


class SN_PanelSearchPropertyGroup(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Name", default="")
    identifier: bpy.props.StringProperty(name="Identifier",default="")


class SN_UiPanelNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node to create a panel in the user interface'''
    bl_idname = 'SN_UiPanelNode'
    bl_label = "Panel"
    bl_icon = node_icons["INTERFACE"]
    bl_width_default = 310

    def getSpace(self):
        if len(bpy.context.scene.sn_space_properties) == 0:
            for type_name in dir(bpy.types):
                type_name = eval("bpy.types."+type_name)
                if bpy.types.Panel in type_name.__bases__:
                    name = type_name.bl_space_type.replace("_", " ")
                    name = name.title()
                    identifier = type_name.bl_space_type
                    if not name in bpy.context.scene.sn_space_properties:
                        item = bpy.context.scene.sn_space_properties.add()
                        item.identifier = identifier
                        item.name = name


    def getRegion(self, context):
        self.sn_region_properties.clear()
        for type_name in dir(bpy.types):
            type_name = eval("bpy.types."+type_name)
            if bpy.types.Panel in type_name.__bases__:
                if type_name.bl_space_type == bpy.context.scene.sn_space_properties[self.space_type_name].identifier:
                    name = type_name.bl_region_type.replace("_", " ")
                    name = name.title()
                    identifier = type_name.bl_region_type
                    if not name in self.sn_region_properties:
                        item = self.sn_region_properties.add()
                        item.identifier = identifier
                        item.name = name

    def getContext(self, context):
        self.getCategory(context)
        self.sn_context_properties.clear()
        for type_name in dir(bpy.types):
            type_name = eval("bpy.types."+type_name)
            if bpy.types.Panel in type_name.__bases__:
                if type_name.bl_region_type == self.sn_region_properties[self.region_type_name].identifier:
                    try:
                        name = type_name.bl_context
                    except AttributeError:
                        name = ""
                    if name != "":
                        if not name.title() in self.sn_context_properties:
                            item = self.sn_context_properties.add()
                            item.identifier = name
                            item.name = name.title()
    

    def getCategory(self, context):
        self.sn_category_properties.clear()
        for type_name in dir(bpy.types):
            type_name = eval("bpy.types."+type_name)
            if bpy.types.Panel in type_name.__bases__:
                if type_name.bl_region_type == self.sn_region_properties[self.region_type_name].identifier:
                    try:
                        name = type_name.bl_category
                    except AttributeError:
                        name = ""
                    if name != "":
                        if not name.title() in self.sn_category_properties:
                            item = self.sn_category_properties.add()
                            item.identifier = name
                            item.name = name.title()


    sn_region_properties: bpy.props.CollectionProperty(type=SN_PanelSearchPropertyGroup)
    sn_context_properties: bpy.props.CollectionProperty(type=SN_PanelSearchPropertyGroup)
    sn_category_properties: bpy.props.CollectionProperty(type=SN_PanelSearchPropertyGroup)

    panel_name: bpy.props.StringProperty(default="New Panel",name="Panel name",description="Name of the panel", update=update_socket_autocompile)
    default_closed: bpy.props.BoolProperty(default=True,name="Default Closed",description="Panel is closed by default", update=update_socket_autocompile)
    hide_header: bpy.props.BoolProperty(default=False,name="Hide Header",description="Hide the Header", update=update_socket_autocompile)
    custom: bpy.props.BoolProperty(default=False,name="Custom Category",description="The panel is custom", update=update_socket_autocompile)

    space_type_name: bpy.props.StringProperty(name="Space Type",description="The space where the panel is going to be used in", update=getRegion)
    region_type_name: bpy.props.StringProperty(name="Region Type", description="The region where the panel is going to be used in", update=getContext)
    context_name: bpy.props.StringProperty(name="Context", description="The context at which your panel shows up", update=update_socket_autocompile)
    category_name: bpy.props.StringProperty(name="Category", description="The name of category", update=update_socket_autocompile)

    def init(self, context):
        self.getSpace()
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.inputs.new('SN_LayoutSocket', "Layout")
        self.inputs.new('SN_BooleanSocket', "Should display").value=True
        self.inputs.new('SN_IntSocket', "Order")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self,"panel_name",text="Name")
        layout.prop_search(self,"space_type_name", context.scene,"sn_space_properties",text="Space")
        layout.prop_search(self,"region_type_name", self,"sn_region_properties",text="Region")
        if len(self.sn_context_properties) > 0:
            layout.prop_search(self,"context_name", self,"sn_context_properties",text="Context")
        if len(self.sn_category_properties) > 0:
            layout.prop(self, "custom")
            if self.custom:
                layout.prop(self, "category_name", text="Category")
            else:
                layout.prop_search(self,"category_name", self,"sn_category_properties",text="Category")
        layout.prop(self, "default_closed")
        layout.prop(self, "hide_header")

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

        space_type = "VIEW_3D"
        region_type = "HEADER"
        if self.space_type_name == "" or self.region_type_name == "":
            errors.append("no_location_panel")
        elif not self.region_type_name in self.sn_region_properties:
            errors.append("wrong_location_panel")
        else:
            space_type = bpy.context.scene.sn_space_properties[self.space_type_name].identifier
            region_type = self.sn_region_properties[self.region_type_name].identifier

        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname == "SN_UiPanelNode":
                if self.name != node.name:
                    if self.panel_name == node.panel_name:
                        errors.append("same_name_panel")

        if self.panel_name == "":
            errors.append("no_name_panel")

        pollValue, error = get_input_value(self, "Should display", ["SN_BooleanSocket"])
        errors+=error

        orderValue, error = get_input_value(self, "Order", ["SN_NumberSocket", "SN_IntSocket"])
        errors+=error

        options = self.options()

        if self.category_name != "":
            if self.custom:
                panelCategory = "_INDENT_bl_category = '" + self.category_name + "'\n"
            elif not self.category_name in self.sn_category_properties:
                panelCategory = ""
                errors.append("wrong_location_panel")
            else:
                panelCategory = "_INDENT_bl_category = '" + self.sn_category_properties[self.category_name].identifier + "'\n"
        else:
            panelCategory = ""

        if self.context_name != "":
            panelContext = "_INDENT_bl_context = '" + self.sn_context_properties[self.context_name].identifier + "'\n\n"
        else:
            panelContext = "\n\n"

        idname = "SN_PT_" + self.panel_name.title().replace(" ","")
        header = ["class " + idname + "(bpy.types.Panel):\n",
                "_INDENT_bl_label = '"+self.panel_name+"'\n",
                "_INDENT_bl_idname = '" + idname + "'\n",
                options,
                "_INDENT_bl_order = int(", orderValue, ")\n",
                "_INDENT_bl_space_type = '", space_type, "'\n",
                "_INDENT_bl_region_type = '", region_type, "'\n",
                panelCategory,
                panelContext,
                "_INDENT_@classmethod\n",
                "_INDENT_def poll(self, context):\n",
                "_INDENT__INDENT_return ", pollValue ,"\n\n",
                "_INDENT_def draw(self, context):\n",
                "_INDENT__INDENT_layout = self.layout\n"]

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