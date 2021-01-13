import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_SubmenuNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SubmenuNode"
    bl_label = "Submenu"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    
    def update_picked(self,context):
        if self.picked:
            self.menu = self.picked
            self.picked = ""
            
    def update_use_internal(self,context):
        self.menu = ""
    
    
    menu: bpy.props.StringProperty()
    
    picked: bpy.props.StringProperty(update=update_picked)

    use_internal: bpy.props.BoolProperty(name="Use Internal",
                                         description="Uses the internal ones from blender instead of your custom ones",
                                         default=False,
                                         update=update_use_internal)


    def on_create(self,context):
        self.add_interface_input("Interface").mirror_name = True
        self.add_string_input("Text")
        self.add_icon_input("Icon")
        
        
    def draw_node(self,context,layout):
        row = layout.row(align=True)
        if self.use_internal:
            name = self.menu.replace("_"," ").title() if self.menu else "Pick Menu"
            op = row.operator("sn.pick_interface",text=name,icon="EYEDROPPER")
            op.node = self.name
            op.selection = "MENUS"
            row.prop(self,"use_internal",text="",icon="BLENDER",invert_checkbox=True)
        else:
            row.prop_search(self,"menu",self.addon_tree.sn_nodes["SN_MenuNode"],"items",text="",icon="VIEWZOOM")
            row.prop(self,"use_internal",text="",icon_value=bpy.context.scene.sn_icons[ "serpens" ].icon_id)
    

    def code_evaluate(self, context, touched_socket):
        
        menu = self.menu
        if not self.use_internal:
            if self.menu in self.addon_tree.sn_nodes["SN_MenuNode"].items:
                menu = self.addon_tree.sn_nodes["SN_MenuNode"].items[self.menu].node().idname()
                
        if menu:

            layout = touched_socket.links[0].from_node.what_layout(touched_socket.links[0].from_socket)

            return {
                "code": f"""
                        {layout}.menu("{menu}",text={self.inputs["Text"].code()},icon_value={self.inputs["Icon"].code()})
                        """
            }