import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ..node_utility import register_dynamic_input, get_input_value
from ...node_sockets import update_socket_autocompile


# https://docs.blender.org/api/current/bpy.types.Panel.html

# bl_context
# bl_order

# draw_header(context):
#    draw a header for the panel
# draw_header_preset(context):
#    draw elements for presets for the header


class SN_UiPanelNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node to create a panel in the user interface'''
    bl_idname = 'SN_UiPanelNode'
    bl_label = "Panel"
    bl_icon = node_icons["INTERFACE"]
    bl_width_default = 200

    panel_name: bpy.props.StringProperty(default="New Panel",name="Panel name",description="Name of the panel", update=update_socket_autocompile)
    default_closed: bpy.props.BoolProperty(default=True,name="Default Closed",description="Panel is closed by default", update=update_socket_autocompile)
    hide_header: bpy.props.BoolProperty(default=False,name="Hide Header",description="Hide the Header", update=update_socket_autocompile)
    space_type_name: bpy.props.EnumProperty(items=[("VIEW_3D", "3D Viewport", "3D Viewport"),
                                              ("IMAGE_EDITOR", "UV/Image Editor", "View and edit images and UV Maps"), 
                                              ("NODE_EDITOR", "Node Editor", "Editor for node-based shading and compositing tools"), 
                                              ("SEQUENCE_EDITOR", "Video Sequencer", "Video editing tools"), 
                                              ("CLIP_EDITOR", "Movie Clip Editor", "Motion tracking tools"), 
                                              ("DOPESHEET_EDITOR", "Dope Sheet", "Adjust timing of keyframes"), 
                                              ("GRAPH_EDITOR", "Graph Editor", "Edit drivers and keyframe interpolation"), 
                                              ("NLA_EDITOR", "Nonlinear Animation", "Combine and layer Actions"), 
                                              ("TEXT_EDITOR", "Text Editor", "Edit scripts and in-file documentation"), 
                                              ("CONSOLE", "Python Console", "Interactive programmatic console for advanced editing and script development"), 
                                              ("INFO", "Info", "Log of operations, warnings and error messages"), 
                                              ("TOPBAR", "Top Bar", "Global bar at the top of the screen for global per-window settings"), 
                                              ("STATUSBAR", "Status Bar", "Global bar at the bottom of the screen for general status information"), 
                                              ("OUTLINER", "Outliner", "Overview of scene graph and all available data-blocks"), 
                                              ("PROPERTIES", "Properties", "Edit properties of active object and related data-blocks"), 
                                              ("FILE_BROWSER", "File Browser", "Browse for files and assets"), 
                                              ("PREFERENCES", "Preferences", "Edit persistent configuration settings")],
                                       name="Space Type",description="The space where the panel is going to be used in", update=update_socket_autocompile)

    region_type_name: bpy.props.EnumProperty(items=[("WINDOW", "Window", ""),
                                               ("HEADER", "Header", ""),
                                               ("CHANNELS", "Channels", ""),
                                               ("TEMPORARY", "Temporary", ""),
                                               ("UI", "User Interface", ""),
                                               ("TOOLS", "Tools", ""),
                                               ("TOOL_PROPS", "Tool Properties", ""),
                                               ("PREVIEW", "Preview", ""),
                                               ("HUD", "Hud", ""),
                                               ("NAVIGATION_BAR", "Navigation Bar", ""),
                                               ("EXECUTE", "Execute", ""),
                                               ("FOOTER", "Footer", ""),
                                               ("TOOL_HEADER", "Tool Header", "")], 
                                        name="Region Type", description="The region where the panel is going to be used in", update=update_socket_autocompile)

    category: bpy.props.StringProperty(name="Category", description="The name of category", update=update_socket_autocompile)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.inputs.new('SN_LayoutSocket', "Layout")
        self.inputs.new('SN_BooleanSocket', "Should display").value=True
        self.inputs.new('SN_NumberSocket', "Order")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self,"panel_name",text="Name")
        layout.prop(self,"space_type_name")
        layout.prop(self,"region_type_name")
        layout.prop(self,"category")
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
        pollValue, error = get_input_value(self, "Should display", "SN_BooleanSocket")
        errors+=error
        orderValue, error = get_input_value(self, "Order", "SN_NumberSocket")
        errors+=error
        options = self.options()
        idname = "SN_PT_" + self.panel_name.title().replace(" ","")
        header = ["class " + idname + "(bpy.types.Panel):\n",
                "_INDENT_bl_label = '"+self.panel_name+"'\n",
                "_INDENT_bl_idname = '" + idname + "'\n",
                options,
                "_INDENT_bl_order = int(", orderValue, ")\n",
                "_INDENT_bl_space_type = '", self.space_type_name, "'\n",
                "_INDENT_bl_region_type = '", self.region_type_name, "'\n",
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