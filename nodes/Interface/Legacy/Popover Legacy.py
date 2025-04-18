import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_PopoverNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_PopoverNode"
    bl_label = "Popover (Legacy)"
    bl_width_default = 200
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_interface_input()
        self.add_string_input("Label")
        self.add_icon_input()
        
        
    parent_type: bpy.props.EnumProperty(name="Parent Type",
                                description="Use a custom panel as a parent",
                                items=[("BLENDER", "Blender", "Blender", "BLENDER", 0),
                                        ("CUSTOM", "Custom", "Custom", "FILE_SCRIPT", 1)],
                                update=SN_ScriptingBaseNode._evaluate)

    panel_parent: bpy.props.StringProperty(default="EEVEE_MATERIAL_PT_surface",
                                    name="Parent",
                                    description="The panel id this subpanel should be shown in",
                                    update=SN_ScriptingBaseNode._evaluate)
    
    
    ref_ntree: bpy.props.PointerProperty(type=bpy.types.NodeTree,
                                name="Panel Node Tree",
                                description="The node tree to select the panel from",
                                poll=SN_ScriptingBaseNode.ntree_poll,
                                update=SN_ScriptingBaseNode._evaluate)
    
    ref_SN_PanelNode: bpy.props.StringProperty(name="Panel",
                                description="The panel to display with this popover",
                                update=SN_ScriptingBaseNode._evaluate)
    
    def on_ref_update(self, node, data=None):
        if node.bl_idname == "SN_PanelNode":
            self._evaluate(bpy.context)


    def evaluate(self, context):
        if self.parent_type == "CUSTOM":
            if self.ref_ntree and self.ref_SN_PanelNode in self.ref_ntree.nodes:
                node = self.ref_ntree.nodes[self.ref_SN_PanelNode]
                self.code = f"""
                    {self.active_layout}.popover('{node.last_idname}', text={self.inputs['Label'].python_value}, icon_value={self.inputs['Icon'].python_value})
                """
        
        else:
            self.code = f"""
                {self.active_layout}.popover('{self.panel_parent}', text={self.inputs['Label'].python_value}, icon_value={self.inputs['Icon'].python_value})
            """


    def draw_node(self, context, layout):
        row = layout.row(align=True)
        if self.parent_type == "CUSTOM":
            row.prop_search(self, "ref_ntree", bpy.data, "node_groups", text="")
            subrow = row.row(align=True)
            subrow.enabled = self.ref_ntree != None
            parent_tree = self.ref_ntree if self.ref_ntree else self.node_tree
            subrow.prop_search(self, "ref_SN_PanelNode", parent_tree.node_collection("SN_PanelNode"), "refs", text="", icon="VIEWZOOM")
        else:
            op = row.operator("sn.activate_subpanel_picker", text=f"{self.panel_parent.replace('_PT_', ' ').replace('_', ' ').title()}", icon="EYEDROPPER")
            op.node_tree = self.node_tree.name
            op.node = self.name
            op.allow_subpanels = True
            
        row.prop(self, "parent_type", text="", icon_only=True)
        

    def draw_node_panel(self, context, layout):
        layout.prop(self, "panel_parent")