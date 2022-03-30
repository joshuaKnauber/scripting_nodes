import bpy
from ..base_node import SN_ScriptingBaseNode
from ...utils import get_python_name



class SN_PanelNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PanelNode"
    bl_label = "Panel"
    bl_width_default = 200
    layout_type = "layout"
    is_trigger = True
    node_color = "INTERFACE"
    

    def on_create(self, context):
        self.add_boolean_input("Hide")
        self.add_interface_output("Panel")
        self.add_dynamic_interface_output("Panel")
        self.add_dynamic_interface_output("Header")
        self.ref_ntree = self.node_tree
        
        
    def update_from_parent(self, parent):
        """ Update this subpanels nodes values from the parent node """
        self["space"] = parent.space
        self["region"] = parent.region
        self["context"] = parent.context


    def update_custom_parent(self, context):
        """ Updates the nodes settings when a new parent panel is selected """
        if self.ref_ntree and self.ref_SN_PanelNode in self.ref_ntree.nodes:
            parent = self.ref_ntree.nodes[self.ref_SN_PanelNode]
            self.update_from_parent(parent)
        self._evaluate(context)
        
        
    def on_ref_update(self, node, data=None):
        """ Called when a parent panel is updated, updates this nodes settings """
        if self.is_subpanel:
            if node.node_tree == self.ref_ntree and node.name == self.ref_SN_PanelNode:
                self.update_from_parent(node)
                self._evaluate(bpy.context)
                    
                    
    def update_is_subpanel(self, context):
        """ Updates the compile order when turned into a subpanel """
        if self.is_subpanel:
            self["parent_type"] = "BLENDER"
            self["ref_SN_PanelNode"] = ""
            self["space"] = "PROPERTIES"
            self["region"] = "WINDOW"
            self["context"] = "render"
            self.order = 1
        else:
            self["space"] = "VIEW_3D"
            self["region"] = "UI"
            self["context"] = ""
            self.order = 0
        self._evaluate(context)


    panel_label: bpy.props.StringProperty(default="New Panel",
                                    name="Label",
                                    description="The label of your panel",
                                    update=SN_ScriptingBaseNode._evaluate)

    space: bpy.props.StringProperty(default="VIEW_3D",
                                    name="Space",
                                    description="The space your panel is in",
                                    update=SN_ScriptingBaseNode._evaluate)

    region: bpy.props.StringProperty(default="UI",
                                    name="Region",
                                    description="The region your panel is in",
                                    update=SN_ScriptingBaseNode._evaluate)

    context: bpy.props.StringProperty(default="",
                                    name="Context",
                                    description="The context your panel is in",
                                    update=SN_ScriptingBaseNode._evaluate)

    category: bpy.props.StringProperty(default="New Category",
                                    name="Category",
                                    description="The category your panel is in (Only relevant if in an N-Panel)",
                                    update=SN_ScriptingBaseNode._evaluate)

    panel_order: bpy.props.IntProperty(default=0, min=0,
                                name="Order",
                                description="The order of your panel compared to other custom panels",
                                update=SN_ScriptingBaseNode._evaluate)

    hide_header: bpy.props.BoolProperty(default=False,
                                    name="Hide Header",
                                    description="Hide the panels header",
                                    update=SN_ScriptingBaseNode._evaluate)

    expand_header: bpy.props.BoolProperty(default=False,
                                    name="Expand Header",
                                    description="Expands the header to fill the full panel width",
                                    update=SN_ScriptingBaseNode._evaluate)

    default_closed: bpy.props.BoolProperty(default=False,
                                    name="Default Closed",
                                    description="Closes the panel by default",
                                    update=SN_ScriptingBaseNode._evaluate)

    is_subpanel: bpy.props.BoolProperty(default=False,
                                    name="Is Subpanel",
                                    description="If this panel should be a subpanel",
                                    update=update_is_subpanel)

    panel_parent: bpy.props.StringProperty(default="RENDER_PT_context",
                                    name="Parent",
                                    description="The panel id this subpanel should be shown in",
                                    update=SN_ScriptingBaseNode._evaluate)

    parent_type: bpy.props.EnumProperty(name="Parent Type",
                                    description="Use a custom panel as a parent",
                                    items=[("BLENDER", "Blender", "Blender", "BLENDER", 0),
                                           ("CUSTOM", "Custom", "Custom", "FILE_SCRIPT", 1)],
                                    update=SN_ScriptingBaseNode._evaluate)
    
    ref_SN_PanelNode: bpy.props.StringProperty(name="Custom Parent",
                                    description="The panel used as a custom parent panel for this subpanel",
                                    update=update_custom_parent)
    
    ref_ntree: bpy.props.PointerProperty(type=bpy.types.NodeTree,
                                    name="Panel Node Tree",
                                    description="The node tree to select the panel from",
                                    poll=SN_ScriptingBaseNode.ntree_poll,
                                    update=SN_ScriptingBaseNode._evaluate)

    idname_override: bpy.props.StringProperty(default="",
                                    name="Idname Override",
                                    description="Use this if you want to define the idname of this panel yourself",
                                    update=SN_ScriptingBaseNode._evaluate)


    
    last_idname: bpy.props.StringProperty(name="Last Idname",
                                    description="The last idname that this panel had when it was compiled",
                                    default="")

    def update_idname(self):
        py_name = get_python_name(self.panel_label)
        alt_py_name = get_python_name(self.name)
        idname = f"SNA_PT_{py_name.upper() if py_name else alt_py_name}_{self.uuid}"
        if self.idname_override:
            idname = self.idname_override
        self.last_idname = idname
        self.trigger_ref_update()


    def evaluate(self, context):
        self.update_idname()
        
        options = []
        if self.hide_header: options.append("'HIDE_HEADER'")
        if self.expand_header: options.append("'HEADER_LAYOUT_EXPAND'")
        if self.default_closed: options.append("'DEFAULT_CLOSED'")
        
        parent = ""
        if self.is_subpanel:
            if self.parent_type == "BLENDER":
                parent = self.panel_parent
            elif self.ref_ntree and self.ref_SN_PanelNode in self.ref_ntree.nodes:
                parent_node = self.ref_ntree.nodes[self.ref_SN_PanelNode]
                parent = parent_node.last_idname
                
        self.code = f"""
                    class {self.last_idname}(bpy.types.Panel):
                        bl_label = '{self.panel_label}'
                        bl_idname = '{self.last_idname}'
                        bl_space_type = '{self.space}'
                        bl_region_type = '{self.region}'
                        bl_context = '{self.context}'
                        {f"bl_category = '{self.category}'" if self.category and not parent else ""}
                        bl_order = {self.panel_order}
                        {f"bl_options = {{{', '.join(options)}}}" if options else ""}
                        {f"bl_parent_id = '{parent}'" if self.is_subpanel and parent else ""}

                        @classmethod
                        def poll(cls, context):
                            return not ({self.inputs["Hide"].python_value})
                        
                        def draw_header(self, context):
                            layout = self.layout
                            {self.indent([out.python_value for out in filter(lambda out: out.name=='Header' and not out.dynamic, self.outputs)], 7)}

                        def draw(self, context):
                            layout = self.layout
                            {self.indent([out.python_value for out in filter(lambda out: out.name=='Panel' and not out.dynamic, self.outputs)], 7)}
                    """

        if self.is_subpanel and parent and not context.scene.sn.is_exporting:
            self.code_register = f"if '{parent}' in globals(): bpy.utils.register_class({self.last_idname})"
            self.code_unregister = f"if '{parent}' in globals(): bpy.utils.unregister_class({self.last_idname})"
        else:
            self.code_register = f"bpy.utils.register_class({self.last_idname})"
            self.code_unregister = f"bpy.utils.unregister_class({self.last_idname})"


    def draw_node(self, context, layout):
        if not self.is_subpanel:
            row = layout.row(align=True)
            row.scale_y = 1.4
            op = row.operator("sn.activate_panel_picker", text=f"{self.space.replace('_', ' ').title()} {self.region.replace('_', ' ').title()} {self.context.replace('_', ' ').title()}", icon="EYEDROPPER")
            op.node_tree = self.node_tree.name
            op.node = self.name
        else:
            row = layout.row(align=True)
            if self.parent_type == "BLENDER":
                op = row.operator("sn.activate_subpanel_picker", text=f"{self.panel_parent.replace('_PT_', ' ').replace('_', ' ').title()}", icon="EYEDROPPER")
                op.node_tree = self.node_tree.name
                op.node = self.name
            else:
                subrow = row.row()
                subrow.enabled = self.ref_ntree != None and self.ref_SN_PanelNode in self.ref_ntree.nodes
                op = subrow.operator("sn.find_node", text="", icon="RESTRICT_SELECT_OFF", emboss=False)
                op.node_tree = self.ref_ntree.name if self.ref_ntree else ""
                op.node = self.ref_SN_PanelNode
            
                parent_tree = self.ref_ntree if self.ref_ntree else self.node_tree
                row.prop_search(self, "ref_ntree", bpy.data, "node_groups", text="")
                subrow = row.row(align=True)
                subrow.enabled = self.ref_ntree != None
                subrow.prop_search(self, "ref_SN_PanelNode", bpy.data.node_groups[parent_tree.name].node_collection(self.bl_idname), "refs", text="")
                if self.ref_SN_PanelNode == self.name and self.ref_ntree == self.node_tree:
                    layout.label(text="Can't use self as panel parent!", icon="ERROR")

            row.prop(self, "parent_type", text="", icon_only=True)
        
        layout.prop(self, "is_subpanel")

        layout.prop(self, "name")
        layout.prop(self, "panel_label")
        if not self.is_subpanel:
            layout.prop(self, "category")

        layout.prop(self, "panel_order")
        layout.prop(self, "hide_header")
        layout.prop(self, "expand_header")
        layout.prop(self, "default_closed")

        
    def draw_node_panel(self, context, layout):
        col = layout.column()
        col.enabled = not self.is_subpanel
        col.prop(self, "space")
        col.prop(self, "region")
        col.prop(self, "context")
        row = layout.row()
        row.enabled = self.is_subpanel
        row.prop(self, "panel_parent")
        layout.prop(self, "idname_override")