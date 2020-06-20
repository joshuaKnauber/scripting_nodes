import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons
from random import randint


class PanelItemsProperties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    idname: bpy.props.StringProperty()

bpy.utils.register_class(PanelItemsProperties)

class SN_AppendPanel(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_AppendPanel"
    bl_label = "Append Panel"
    bl_width_default = 230
    bl_icon = node_icons["INTERFACE"]

    _should_be_registered = True
    _dynamic_layout_sockets = True

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    panels: bpy.props.CollectionProperty(type=PanelItemsProperties)

    def _update_panel_items(self):
        """ update the panel items for the given region and space type """
        panels = self.UiLocationHandler.get_panels(self.space_type,self.region_type)
        self.panels.clear()
        for panel in panels:
            item = self.panels.add()
            item.name = panel[0]
            item.idname = panel[1]

    def update_region_type(self,context):
        """ called when the region type is updated """
        self.inputs[0].hide = not self.UiLocationHandler.space_region_has_categories(self.space_type,self.region_type)
        self._update_panel_items()
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

    panel_uid: bpy.props.StringProperty(default="")

    panel_name: bpy.props.StringProperty(default="")

    def init(self, context):
        self.panel_uid = str(randint(1111,9999))
        self._update_panel_items()

        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

    def draw_buttons(self, context, layout):
        layout.operator("scripting_nodes.panel_picker",icon="EYEDROPPER", text="Panel Location").node_name = self.name
        layout.prop(self, "space_type")
        layout.prop(self, "region_type")

        layout.prop_search(self,"panel_name", self, "panels", text="")

    def evaluate(self, output):
        error_list = []
        
        layouts, errors = self.SocketHandler.get_layout_values(self)
        error_list += errors

        return {
            "blocks": [
                {
                    "lines": [
                        ["def append_panel_"+self.panel_uid+"(self, context):"]
                    ],
                    "indented": [
                        ["layout = self.layout"],
                        layouts
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
        if self.panel_name:
            return ["bpy.types."+self.panels[self.panel_name].idname+".append("+"append_panel_"+self.panel_uid+")"]
        return []

    def get_unregister_block(self):
        if self.panel_name:
            return ["bpy.types."+self.panels[self.panel_name].idname+".remove("+"append_panel_"+self.panel_uid+")"]
        return []