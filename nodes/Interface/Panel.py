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
    
    docs = {
        "description": "This node can be used to make a panel or a subpanel in the blender user interface. Use the picker button to select the location of the panel in the UI.\nIf you want to add it to a N-Panel, click the Picker button and go to the Misc category in the N-Panel.",
        "settings": "- Is Subpanel: If this is enabled the this panel node becomes a subpanel inside another panel."
                    + "- Label: The label is what gets displayed in the header of the panel.\n"
                    + "- Category: If your panel is in an N-Panel, this represents the tab your panel goes in. Otherwise you can ignore this.\n"
                    + "- Order: If you have multiple panels you can order them with this number. The first panel is 0. You can't always sort your panel above blender internal panels.\n"
                    + "- Hide Header: Hides the header of your panel completely. Blender may also show your panel at the top of the panel stack.\n"
                    + "- Expand Header: Applies normal layouts to your header. This will expand inputs and labels and let you align things other than to the left.\n"
                    + "- Default Closed: Closes your panel by default.\n",
        "inputs": "- Hide: If this receives True (enabled), your panel will be hidden from the UI.",
        "outputs": "- Panel: The panel outputs are the starting point for you to add elements to your interface.\n"
                    + "- Header: The header outputs can add elements to your panels header. You can leave the label empty and add it back with a label."
    }

    def on_create(self, context):
        self.add_boolean_input("Hide")
        self.add_interface_output("Panel")
        self.add_dynamic_interface_output("Panel")
        self.add_dynamic_interface_output("Header")

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
                                    description="The category your panel is in",
                                    update=SN_ScriptingBaseNode._evaluate)

    order: bpy.props.IntProperty(default=0, min=0,
                                name="Order",
                                description="The order of your panel compared to the other panels",
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
                                    update=SN_ScriptingBaseNode._evaluate)

    panel_parent: bpy.props.StringProperty(default="EEVEE_MATERIAL_PT_surface",
                                    name="Parent",
                                    description="The panel id this subpanel should be shown in",
                                    update=SN_ScriptingBaseNode._evaluate)

    idname_override: bpy.props.StringProperty(default="",
                                    name="Idname Override",
                                    description="Use this if you want to define the idname of this panel yourself",
                                    update=SN_ScriptingBaseNode._evaluate)


    def evaluate(self, context):
        py_name = get_python_name(self.panel_label)
        alt_py_name = get_python_name(self.name)
        idname = f"SNA_PT_{py_name.upper() if py_name else alt_py_name}_{self.space}_{self.region}{'_'+self.context if self.context else ''}"
        if self.idname_override:
            idname = self.idname_override

        options = []
        if self.hide_header: options.append("'HIDE_HEADER'")
        if self.expand_header: options.append("'HEADER_LAYOUT_EXPAND'")
        if self.default_closed: options.append("'DEFAULT_CLOSED'")

        self.code = f"""
                    class {idname}(bpy.types.Panel):
                        bl_label = "{self.panel_label}"
                        bl_idname = "{idname}"
                        bl_space_type = '{self.space}'
                        bl_region_type = '{self.region}'
                        {f"bl_context = '{self.context}'" if self.context else ""}
                        {f"bl_category = '{self.category}'" if self.category else ""}
                        bl_order = {self.order}
                        {f"bl_options = {{{', '.join(options)}}}" if options else ""}
                        {f"bl_parent_id = '{self.panel_parent}'" if self.is_subpanel and self.panel_parent else ""}

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

        self.code_register = f"bpy.utils.register_class({idname})"
        self.code_unregister = f"bpy.utils.unregister_class({idname})"


    def draw_node(self, context, layout):
        row = layout.row()
        row.scale_y = 1.3

        if not self.is_subpanel:
            op = row.operator("sn.activate_panel_picker", text=f"{self.space.replace('_', ' ').title()} {self.region.replace('_', ' ').title()} {self.context.replace('_', ' ').title()}", icon="EYEDROPPER")
            op.node_tree = self.node_tree.name
            op.node = self.name
        else:
            op = row.operator("sn.activate_subpanel_picker", text=f"{self.panel_parent.replace('_PT_', ' ').replace('_', ' ').title()}", icon="EYEDROPPER")
            op.node_tree = self.node_tree.name
            op.node = self.name
        
        layout.prop(self, "is_subpanel")

        layout.prop(self, "panel_label")
        if not self.is_subpanel:
            layout.prop(self, "category")

        layout.prop(self, "order")
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