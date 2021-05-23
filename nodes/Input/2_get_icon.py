import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_OT_SetIcon(bpy.types.Operator):
    bl_idname = "sn.set_icon"
    bl_label = "Set Icon"
    bl_description = "Sets this icon"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    node: bpy.props.StringProperty()
    icon: bpy.props.IntProperty()

    def execute(self, context):
        context.space_data.node_tree.nodes[self.node].icon = self.icon
        context.area.tag_redraw()
        return {"FINISHED"}



class SN_OT_SelectIcon(bpy.types.Operator):
    bl_idname = "sn.select_icon"
    bl_label = "Select Icon"
    bl_description = "Shows you a selection of all blender icons"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    bl_property = "icon_search"
    
    node: bpy.props.StringProperty()
    icon_search: bpy.props.StringProperty(name="Search", options={"SKIP_SAVE"})

    def execute(self, context):
        return {"FINISHED"}
    
    def invoke(self,context,event):
        return context.window_manager.invoke_popup(self, width=800)
    
    def draw(self,context):
        layout = self.layout
        icons = bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items
        node = context.space_data.node_tree.nodes[self.node]
        
        row = self.layout.row()
        row.prop(self,"icon_search",text="",icon="VIEWZOOM")

        grid = self.layout.grid_flow(align=True,even_columns=True, even_rows=True)
        for icon in icons:
            if self.icon_search.lower() in icon.name.lower() or not self.icon_search:
                op = grid.operator("sn.set_icon",text="", icon_value=icon.value, emboss=node.icon==icon.value)
                op.node = self.node
                op.icon = icon.value



class SN_GetIconNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetIconNode"
    bl_label = "Icon"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
        "imperative_once": True
    }
    
    def update_source(self,context):
        if self.icon_source == "BLENDER":
            self.outputs[0].is_expression = False
        elif self.custom_icon != "" and self.custom_icon in self.addon_tree.sn_icons:
            self.outputs[0].is_expression = True
        self.auto_compile(context)
    
    icon_source: bpy.props.EnumProperty(name="Icon Source",
                                        update=update_source,
                                        description="The source of the icons",
                                        items=[("BLENDER","Blender","Blender",0),
                                                ("CUSTOM","Custom","Custom",1)])

    
    icon: bpy.props.IntProperty(default=2,update=SN_ScriptingBaseNode.auto_compile)
    custom_icon: bpy.props.StringProperty(default="",update=update_source)


    def on_create(self,context):
        self.add_icon_output("Icon")


    def draw_node(self,context,layout):
        row = layout.row()
        row.scale_y = 1.2
        row.prop(self,"icon_source",expand=True)
        
        row = layout.row()
        addon_tree = context.scene.sn.addon_tree()
        if self.icon_source == "CUSTOM":
            if self.custom_icon in addon_tree.sn_icons and addon_tree.sn_icons[self.custom_icon].image:
                custom_icon = addon_tree.sn_icons[self.custom_icon].image.preview.icon_id
                row.label(icon_value=custom_icon)
                row.prop_search(self,"custom_icon",addon_tree,"sn_icons",text="")
            else:
                row.label(icon="ERROR")
                row.prop_search(self,"custom_icon",addon_tree,"sn_icons",text="")                
        else:
            op = row.operator("sn.select_icon",icon_value=self.icon)
            op.node = self.name


    def code_evaluate(self, context, touched_socket):
        icon = str(self.icon)
        if self.icon_source == "CUSTOM":
            if self.custom_icon and self.custom_icon in self.addon_tree.sn_icons and self.addon_tree.sn_icons[self.custom_icon].image:
                icon = f"bpy.context.scene.{self.addon_tree.sn_graphs[0].short()}_icons['{self.custom_icon}'].icon_id"
            else:
                self.add_error("No Icon", "No Icon selected")
                icon = "2"
        return {
            "code": icon
        }