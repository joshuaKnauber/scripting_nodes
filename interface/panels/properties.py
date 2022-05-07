import bpy
from .property_ui_list import get_selected_property, get_selected_property_offset



class SN_PT_PropertyPanel(bpy.types.Panel):
    bl_idname = "SN_PT_PropertyPanel"
    bl_label = ""
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 1
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Properties")
        layout.operator("wm.url_open", text="", icon="QUESTION", emboss=False).url = "https://joshuaknauber.notion.site/Properties-6f7567be7bff4256b9bb0311e8d79f9d"
    
    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn
        prop = get_selected_property()
        before = get_selected_property_offset(-1)
        after = get_selected_property_offset(1)
        
        # draw property ui list
        row = layout.row(align=False)
        col = row.column(align=True)
        
        if sn.show_property_categories:
            subrow = col.row(align=True)
            subrow.prop(sn, "active_prop_category", text="")
            subrow.operator("sn.edit_property_categories", text="", icon="GREASEPENCIL")

        col.template_list("SN_UL_PropertyList", "Properties", sn, "properties", sn, "property_index", rows=4)
        col.operator("sn.add_property_node_popup", text="Add Node", icon="ADD")
        col = row.column(align=True)
        col.operator("sn.add_property", text="", icon="ADD")
        col.operator("sn.find_property", text="", icon="VIEWZOOM")
        subrow = col.row(align=True)
        subrow.enabled = prop != None
        subrow.operator("sn.remove_property", text="", icon="REMOVE")

        col.separator()
        subrow = col.row(align=True)
        subrow.enabled = before != None and prop != None
        op = subrow.operator("sn.move_property", text="", icon="TRIA_UP")
        op.move_up = True
        subrow = col.row(align=True)
        subrow.enabled = after != None and prop != None
        op = subrow.operator("sn.move_property", text="", icon="TRIA_DOWN")
        op.move_up = False
        layout.separator()
        
        
        if prop:            
            # draw property debug
            if sn.debug_python_properties:
                box = layout.box()
                col = box.column(align=True)
                row = col.row()
                row.enabled = False
                row.label(text="Register")
                for line in prop.register_code.split("\n"):
                    col.label(text=line)
                box = layout.box()
                col = box.column(align=True)
                row = col.row()
                row.enabled = False
                row.label(text="Unregister")
                for line in prop.unregister_code.split("\n"):
                    col.label(text=line)
            
            col = layout.column()
            col.use_property_split = True
            col.use_property_decorate = False

            # draw general property settings
            prop.draw(context, col)
            
            # draw property specific settings
            col.separator()
            prop.settings.draw(context, col)