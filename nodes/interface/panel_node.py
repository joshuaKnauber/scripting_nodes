import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons
from random import randint


class SN_Panel(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_Panel"
    bl_label = "Panel"
    bl_width_default = 230
    bl_icon = node_icons["INTERFACE"]

    _should_be_registered = True
    _dynamic_layout_sockets = True

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def update_region_type(self,context):
        """ called when the region type is updated """
        self.inputs[0].hide = not self.UiLocationHandler.space_region_has_categories(self.space_type,self.region_type)
        self.socket_update(context)

    def get_space_types(self,context):
        return self.UiLocationHandler.space_type_items()
    space_type: bpy.props.EnumProperty(name="Space",description="Space the panel should go in",items=get_space_types,update=socket_update)

    def get_region_types(self,context):
        return self.UiLocationHandler.region_type_items(self.space_type)
    region_type: bpy.props.EnumProperty(name="Region",description="Region the panel should go in",items=get_region_types,update=update_region_type)

    def get_contexts(self,context):
        return self.UiLocationHandler.context_items(self.space_type,self.region_type)
    panel_context: bpy.props.EnumProperty(name="Context",description="Context the panel should go in",items=get_contexts,update=socket_update)

    panel_name: bpy.props.StringProperty(default="New Panel",name="Name",description="Name of the panel",update=socket_update)
    closed_by_default: bpy.props.BoolProperty(default=False,name="Closed By Default",description="Close this panel by default",update=socket_update)
    hide_header: bpy.props.BoolProperty(default=False,name="Hide Header",description="Hide the header of this panel",update=socket_update)

    panel_uid: bpy.props.StringProperty(default="")

    def init(self, context):
        self.panel_uid = str(randint(1111,9999))

        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.inputs.new("SN_StringSocket", "Category").value = "Misc"
        self.update_region_type(context)

        #poll
        self.inputs.new("SN_BooleanSocket", "Hide Panel").value = False

        #bl_order
        self.inputs.new("SN_IntSocket", "Order Index").value = 0

    def draw_buttons(self, context, layout):
        layout.label(text="Location:")
        layout.operator("scripting_nodes.panel_picker",icon="EYEDROPPER").node_name = self.name

        layout.prop(self,"space_type")
        layout.prop(self,"region_type")
        
        if self.UiLocationHandler.context_items(self.space_type,self.region_type):
            layout.prop(self,"panel_context")

        layout.separator()
        layout.label(text="Settings:")
        layout.prop(self,"panel_name")

        layout.prop(self,"closed_by_default")
        layout.prop(self,"hide_header")

    def _get_panel_name(self):
        """ returns the id name of the panel """
        panel_idname = "SN_PT_NewPanel" + self.panel_uid
        errors = []
        if self.panel_name:
            panel_idname = self.ErrorHandler.handle_text(self.panel_name)
            panel_idname = "SN_PT_" + panel_idname.replace(" ", "_").upper() + self.panel_uid
        else:
            errors.append({"error": "no_name_panel", "node": self})
        return panel_idname, errors

    def evaluate(self, output):
        error_list = []

        panel_idname, errors = self._get_panel_name()
        error_list += errors

        panel_name = self.panel_name
        if not panel_name:
            panel_name = "Scripting Nodes Panel"

        category = []
        if self.UiLocationHandler.space_region_has_categories(self.space_type,self.region_type):
            category, errors = self.SocketHandler.socket_value(self.inputs["Category"], as_list=True)
            error_list += errors
            if not category:
                category = "Misc"
            category = ["bl_category = \""] + category + ["\""]

        context = []
        if self.UiLocationHandler.context_items(self.space_type,self.region_type):
            context = ["bl_context = \"", self.panel_context, "\""]

        order, errors = self.SocketHandler.socket_value(self.inputs["Order Index"], as_list=True)
        error_list += errors

        options = []
        if self.closed_by_default and self.hide_header:
            options = ["bl_options = {\"DEFAULT_CLOSED\",\"HIDE_HEADER\"}"]
        elif self.closed_by_default:
            options = ["bl_options = {\"DEFAULT_CLOSED\"}"]
        elif self.hide_header:
            options = ["bl_options = {\"HIDE_HEADER\"}"]

        layouts = []
        for input_socket in self.inputs:
            if input_socket.bl_idname == "SN_LayoutSocket":
                if input_socket.is_linked:
                    layouts.append(input_socket.links[0].from_socket)

        return {
            "blocks": [
                {
                    "lines": [
                        ["class ",panel_idname,"(bpy.types.Panel):"]
                    ],
                    "indented": [
                        ["bl_label = \"",panel_name,"\""],
                        ["bl_idname = \"",panel_idname,"\""],
                        ["bl_space_type = \"",self.space_type,"\""],
                        ["bl_region_type = \"",self.region_type,"\""],
                        context,
                        category,
                        ["bl_order = "] + order,
                        options,
                        [""],
                        {
                            "lines": [
                                ["def draw(self,context):"]
                            ],
                            "indented": [
                                ["layout = self.layout"],
                            ]
                        },
                        {
                            "lines": [],
                            "indented": layouts
                        }
                    ]
                }
            ],
            "errors": error_list
        }

    def layout_type(self):
        return "layout"

    def needed_imports(self):
        return ["bpy"]

    def get_register_block(self):
        idname, _ = self._get_panel_name()
        return ["bpy.utils.register_class("+idname+")"]

    def get_unregister_block(self):
        idname, _ = self._get_panel_name()
        return ["bpy.utils.unregister_class("+idname+")"]