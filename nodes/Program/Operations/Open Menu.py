import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_OpenMenuNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_OpenMenuNode"
    bl_label = "Open Menu"
    node_color = "PROGRAM"
    bl_width_default = 240

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.ref_ntree = self.node_tree

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
                                    description="The menu that should be shown",
                                    update=SN_ScriptingBaseNode._evaluate)
    
    ref_ntree: bpy.props.PointerProperty(type=bpy.types.NodeTree,
                                    name="Menu Node Tree",
                                    description="The node tree to select the menu from",
                                    poll=SN_ScriptingBaseNode.ntree_poll,
                                    update=SN_ScriptingBaseNode._evaluate)
    
    menu_parent: bpy.props.StringProperty(name="Menu",
                                    default="VIEW3D_MT_add",
                                    description="The menu that should be displayed",
                                    update=SN_ScriptingBaseNode._evaluate)

    def evaluate(self, context):
        if self.parent_type == "CUSTOM":
            if self.ref_ntree and self.ref_SN_MenuNode in self.ref_ntree.nodes:
                self.code = f"""
                    bpy.ops.wm.call_menu(name="{self.ref_ntree.nodes[self.ref_SN_MenuNode].idname}")
                    {self.indent(self.outputs[0].python_value, 5)}
                """
        else:
            self.code = f"""
                bpy.ops.wm.call_menu(name="{self.menu_parent}")
                {self.indent(self.outputs[0].python_value, 4)}
            """

    def draw_node(self, context, layout):
        row = layout.row(align=True)
        
        if self.parent_type == "CUSTOM":
            parent_tree = self.ref_ntree if self.ref_ntree else self.node_tree
            row.prop_search(self, "ref_ntree", bpy.data, "node_groups", text="")
            subrow = row.row(align=True)
            subrow.enabled = self.ref_ntree != None
            subrow.prop_search(self, "ref_SN_MenuNode", parent_tree.node_collection("SN_MenuNode"), "refs", text="")
            
            row.prop(self, "parent_type", text="", icon_only=True)
            
            subrow = row.row()
            subrow.enabled = self.ref_ntree != None and self.ref_SN_MenuNode in self.ref_ntree.nodes
            op = subrow.operator("sn.find_node", text="", icon="RESTRICT_SELECT_OFF", emboss=False)
            op.node_tree = self.ref_ntree.name if self.ref_ntree else ""
            op.node = self.ref_SN_MenuNode
        else:
            name = f"{self.menu_parent.replace('_MT_', ' ').replace('_', ' ').title()}"
            op = row.operator("sn.activate_menu_picker", icon="EYEDROPPER", text=name)
            op.node_tree = self.node_tree.name
            op.node = self.name

            row.prop(self, "parent_type", text="", icon_only=True)

        
    def draw_node_panel(self, context, layout):
        layout.prop(self, "menu_parent")