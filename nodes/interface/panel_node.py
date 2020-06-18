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

    def update_region_type(self,context):
        """ called when the region type is updated """
        self.inputs[0].hide = not self.UiLocationHandler.space_region_has_categories(self.space_type,self.region_type)

    def get_space_types(self,context):
        return self.UiLocationHandler.space_type_items()
    space_type: bpy.props.EnumProperty(name="Space",description="Space the panel should go in",items=get_space_types)

    def get_region_types(self,context):
        return self.UiLocationHandler.region_type_items(self.space_type)
    region_type: bpy.props.EnumProperty(name="Region",description="Region the panel should go in",items=get_region_types,update=update_region_type)

    def get_contexts(self,context):
        return self.UiLocationHandler.context_items(self.space_type,self.region_type)
    panel_context: bpy.props.EnumProperty(name="Context",description="Context the panel should go in",items=get_contexts)

    panel_name: bpy.props.StringProperty(default="New Panel",name="Name",description="Name of the panel")

    def socket_update(self, context):
        compiler().socket_update(context)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.inputs.new("SN_StringSocket", "Category").value = "Misc"
        self.update_region_type(context)

        #bl_options
        self.inputs.new("SN_BooleanSocket", "Closed By Default").value = False
        self.inputs.new("SN_BooleanSocket", "Hide Header").value = False

        #poll
        self.inputs.new("SN_BooleanSocket", "Hide Panel").value = False

        #bl_order
        self.inputs.new("SN_IntSocket", "Order Index").value = 0

    def draw_buttons(self, context, layout):
        layout.prop(self,"panel_name")
        layout.prop(self,"space_type")
        layout.prop(self,"region_type")
        
        if self.UiLocationHandler.context_items(self.space_type,self.region_type):
            layout.prop(self,"panel_context")

    def evaluate(self, output):
        error_list = []

        panel_idname = "SN_PT_NewPanel" + str(randint(1111,9999))
        if self.panel_name:
            panel_idname = self.ErrorHandler.handle_text(self.panel_name)
            panel_idname = "SN_PT_" + panel_idname.replace(" ", "_").upper() + str(randint(1111,9999))
        else:
            error_list.append({"error": "no_name_panel", "node": self})

        panel_name = self.ErrorHandler.handle_text(self.panel_name)
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

        return {
            "blocks": [
                {
                    "lines": [
                        ["class ",panel_idname,"(bpy.types.Panel):"]
                    ],
                    "indented": [
                        {
                            ["bl_label = \"",panel_name,"\""],
                            ["bl_order = "] + order,
                            []
                        }
                    ]
                }
            ],
            "errors": error_list
        }

    def needed_imports(self):
        return ["bpy"]

"""
class SN_PT_ErrorLogPanel(bpy.types.Panel):
    bl_label = "Errors"
    bl_order = 2
    bl_idname = "SN_PT_ErrorLogPanel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Visual Scripting"
"""