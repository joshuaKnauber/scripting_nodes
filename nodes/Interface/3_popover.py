import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_PopoverNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PopoverNode"
    bl_label = "Popover"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    
    def update_picked(self,context):
        if self.picked:
            self.panel = self.picked
            self.picked = ""
            
    def update_use_internal(self,context):
        self.panel = ""
    
    
    panel: bpy.props.StringProperty()
    
    picked: bpy.props.StringProperty(update=update_picked)

    use_internal: bpy.props.BoolProperty(name="Use Internal",
                                         description="Uses the internal ones from blender instead of your custom ones",
                                         default=False,
                                         update=update_use_internal)


    def on_create(self,context):
        self.add_required_to_collection(["SN_PanelNode"])
        self.add_interface_input("Interface").mirror_name = True
        self.add_string_input("Text")
        self.add_icon_input("Icon")
        
        
    def draw_node(self,context,layout):
        row = layout.row(align=True)
        if self.use_internal:
            name = self.panel.replace("_"," ").title() if self.panel else "Pick Panel"
            op = row.operator("sn.pick_interface",text=name,icon="EYEDROPPER")
            op.node = self.name
            op.selection = "PANELS"
            row.prop(self,"use_internal",text="",icon="BLENDER",invert_checkbox=True)
        elif "SN_PanelNode" in self.addon_tree.sn_nodes:
            row.prop_search(self,"panel",self.addon_tree.sn_nodes["SN_PanelNode"],"items",text="",icon="VIEWZOOM")
            row.prop(self,"use_internal",text="",icon_value=bpy.context.scene.sn_icons[ "serpens" ].icon_id)
    

    def code_evaluate(self, context, touched_socket):
        
        panel = self.panel
        if not self.use_internal:
            if self.panel in self.addon_tree.sn_nodes["SN_PanelNode"].items:
                panel = self.addon_tree.sn_nodes["SN_PanelNode"].items[self.panel].node().idname()
                
        if panel:

            layout = touched_socket.links[0].from_node.what_layout(touched_socket.links[0].from_socket)

            return {
                "code": f"""
                        {layout}.popover("{panel}",text={self.inputs["Text"].code()},icon_value={self.inputs["Icon"].code()})
                        """
            }
        else:
            self.add_error("No Panel", "No panel selected")
            return {"code": ""}