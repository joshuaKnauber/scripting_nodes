import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_SetIcon(bpy.types.Operator):
    bl_idname = "sn.set_icon"
    bl_label = "Set Icon"
    bl_description = "Sets this icon"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    node: bpy.props.StringProperty()
    icon: bpy.props.StringProperty()

    def execute(self, context):
        context.space_data.node_tree.nodes[self.node].icon = self.icon
        context.area.tag_redraw()
        return {"FINISHED"}



class SN_SelectIcon(bpy.types.Operator):
    bl_idname = "sn.select_icon"
    bl_label = "Select Icon"
    bl_description = "Shows you a selection of all blender icons"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    node: bpy.props.StringProperty()
    icon_search: bpy.props.StringProperty(options={"SKIP_SAVE"})

    def execute(self, context):
        return {"FINISHED"}
    
    def invoke(self,context,event):
        return context.window_manager.invoke_popup(self, width=800)
    
    def draw(self,context):
        layout = self.layout
        icons = bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.keys()
        node = context.space_data.node_tree.nodes[self.node]
        
        row = self.layout.row()
        row.prop(self,"icon_search",text="",icon="VIEWZOOM")

        grid = self.layout.grid_flow(align=True,even_columns=True, even_rows=True)
        for icon in icons:
            if self.icon_search.lower() in icon.lower() or not self.icon_search:
                op = grid.operator("sn.set_icon",text="", icon=icon, emboss=node.icon==icon)
                op.node = self.node
                op.icon = icon



class SN_GetIconNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetIconNode"
    bl_label = "Icon"
    bl_icon = "GRAPH"
    bl_width_default = 200
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
        "imperative_once": True
    }
    
    icon_source: bpy.props.EnumProperty(name="Icon Source",
                                        update=SN_ScriptingBaseNode.update_needs_compile,
                                        description="The source of the icons",
                                        items=[("BLENDER","Blender","Blender","BLENDER",0),
                                                ("CUSTOM","Custom","Custom","FILE_SCRIPT",1)])

    
    icon: bpy.props.StringProperty(default="ERROR",update=SN_ScriptingBaseNode.update_needs_compile)
    custom_icon: bpy.props.StringProperty(default="",update=SN_ScriptingBaseNode.update_needs_compile)


    def on_create(self,context):
        self.add_icon_output("Icon")


    def draw_node(self,context,layout):
        row = layout.row()
        row.scale_y = 1.5
        row.prop(self,"icon_source",expand=True)
        
        row = layout.row()
        addon_tree = context.scene.sn.addon_tree()
        if self.icon_source == "CUSTOM":
            if self.custom_icon in addon_tree.sn_icons and addon_tree.sn_icons[self.custom_icon].image in bpy.data.images:
                custom_icon = bpy.data.images[addon_tree.sn_icons[self.custom_icon].image].preview.icon_id
                row.label(icon_value=custom_icon)
                row.prop_search(self,"custom_icon",addon_tree,"sn_icons",text="")
            else:
                row.label(icon="ERROR")
                row.prop_search(self,"custom_icon",addon_tree,"sn_icons",text="")                
        else:
            op = row.operator("sn.select_icon",icon=self.icon)
            op.node = self.name
            
            
    def code_imperative(self, context, main_tree):
        return {
            "code": f"""
                    def {main_tree.sn_graphs[0].short()}_icon(name, is_custom):
                        if is_custom:
                            if sn_is_dev():
                                for tree in bpy.data.node_groups:
                                    if len(tree.sn_icons):
                                        return str(bpy.data.images[tree.sn_icons[name].image].preview.icon_id)
                            else:
                                if name in bpy.context.scene.{main_tree.sn_graphs[0].short()}_icons:
                                    return str(bpy.context.scene.{main_tree.sn_graphs[0].short()}_icons[name].icon_id)
                            return "ERROR"
                        return name
                    """
        }


    def code_evaluate(self, context, main_tree, touched_socket):
        icon = self.icon
        if self.icon_source == "CUSTOM":
            if self.custom_icon and self.custom_icon in main_tree.sn_icons:
                icon = self.custom_icon
            else:
                icon = "ERROR"
        return {
            "code": f"""
                    {main_tree.sn_graphs[0].short()}_icon("{icon}",{str(self.icon_source == "CUSTOM")})
                    """
        }