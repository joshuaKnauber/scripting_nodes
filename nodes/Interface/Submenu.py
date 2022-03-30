import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_SubmenuNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SubmenuNode"
    bl_label = "Submenu"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        self.add_string_input("Label")
        self.add_icon_input()

    def on_ref_update(self, node, data=None):
        if node.bl_idname in ["SN_PanelNode", "SN_MenuNode", "SN_PieMenuNode"]:
            self._evaluate(bpy.context)
            
    parent_type: bpy.props.EnumProperty(name="Parent Type",
                                    description="Use a custom panel as a parent",
                                    default="CUSTOM",
                                    items=[("BLENDER", "Blender", "Blender", "BLENDER", 0),
                                           ("CUSTOM", "Custom", "Custom", "FILE_SCRIPT", 1)],
                                    update=SN_ScriptingBaseNode._evaluate)
    
    ref_SN_MenuNode: bpy.props.StringProperty(name="Custom Parent",
                                    description="The panel used as a custom parent panel for this subpanel",
                                    update=SN_ScriptingBaseNode._evaluate)
    
    ref_ntree: bpy.props.PointerProperty(type=bpy.types.NodeTree,
                                    name="Panel Node Tree",
                                    description="The node tree to select the panel from",
                                    poll=SN_ScriptingBaseNode.ntree_poll,
                                    update=SN_ScriptingBaseNode._evaluate)
    
    menu_parent: bpy.props.StringProperty(name="Menu",
                                    default="VIEW3D_MT_add",
                                    description="The menu that should be displayed",
                                    update=SN_ScriptingBaseNode._evaluate)

    def evaluate(self, context):
        if self.parent_type == "CUSTOM":
            if self.ref_ntree and self.ref_SN_MenuNode in self.ref_ntree.nodes:
                self.code = f"{self.active_layout}.menu('{self.ref_ntree.nodes[self.ref_SN_MenuNode].idname}', text={self.inputs['Label'].python_value}, icon_value={self.inputs['Icon'].python_value})"
        else:
            self.code = f"{self.active_layout}.menu('{self.menu_parent}', text={self.inputs['Label'].python_value}, icon_value={self.inputs['Icon'].python_value})"

    def draw_node(self, context, layout):
        row = layout.row(align=True)
        
        if self.parent_type == "CUSTOM":
            parent_tree = self.ref_ntree if self.ref_ntree else self.node_tree
            row.prop_search(self, "ref_ntree", bpy.data, "node_groups", text="")
            subrow = row.row(align=True)
            subrow.enabled = self.ref_ntree != None
            subrow.prop_search(self, "ref_SN_MenuNode", parent_tree.node_collection("SN_MenuNode"), "refs", text="")
        else:
            name = f"{self.menu_parent.replace('_MT_', ' ').replace('_', ' ').title()}"
            op = row.operator("sn.activate_menu_picker", icon="EYEDROPPER", text=name)
            op.node_tree = self.node_tree.name
            op.node = self.name

        row.prop(self, "parent_type", text="", icon_only=True)
        
    def draw_node_panel(self, context, layout):
        layout.prop(self, "menu_parent")