import bpy
        
        
        
class SN_PT_navigation_bar(bpy.types.Panel):
    bl_label = "Preferences Navigation"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'NAVIGATION_BAR'
    bl_options = {'HIDE_HEADER'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.sn.hide_preferences

    def draw(self, context):
        layout = self.layout

        layout.operator("wm.url_open", text="How to", icon="QUESTION").url = "https://joshuaknauber.notion.site/Blend-Data-33e9f2ea40f44c2498cb26838662b621"
        layout.separator()

        row = layout.row()
        row.scale_y = 1.4
        row.alert = True
        row.operator("sn.exit_search", text="Exit", icon="PANEL_CLOSE")
        layout.separator()

        layout.label(text="Source:")
        col = layout.column()
        col.scale_y = 1.4
        col.prop(context.scene.sn, "data_category", expand=True)
        layout.separator()
        
        col = layout.column()
        col.label(text="Filter:")
        col.prop(context.scene.sn, "data_filter", expand=True)



class SN_PT_data_search(bpy.types.Panel):
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_label = "Display"
    bl_options = {'HIDE_HEADER'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.sn.hide_preferences
    
    def draw_item(self, sn, layout, prev_items):
        curr_item = prev_items[-1]
        box = layout.box()
        row = box.row()
        if not curr_item.has_properties:
            row.scale_y = 0.65

        if curr_item.has_properties:
            row.prop(curr_item, "expand", text="", icon="DISCLOSURE_TRI_DOWN" if curr_item.expand else "DISCLOSURE_TRI_RIGHT", emboss=False)

        row.label(text=" | ".join(list(map(lambda x: x.name.replace("_", " ").title(), prev_items))))
        row = row.row()
        row.alignment = "RIGHT"
        
        # if curr_item.type == "COLLECTION":
        #     subrow = row.row()
        #     if curr_item.use_string_index:
        #         subrow.prop(curr_item, "index_string", text="")
        #     else:
        #         subrow.prop(curr_item, "index_int", text="")
        #     subrow.prop(curr_item, "use_string_index", text="", icon="SYNTAX_OFF" if curr_item.use_string_index else "DRIVER_TRANSFORM")
        
        subrow = row.row()
        subrow.enabled = False
        subrow.label(text=curr_item.type.replace("_", " ").title())
        
        row.operator("sn.copy_python_name", text="", icon="COPYDOWN", emboss=False).name = curr_item.path
        row.operator("sn.tooltip", text="", icon="QUESTION", emboss=False).text = curr_item.description

        if curr_item.expand:
            row = box.row()
            split = row.split(factor=0.025)
            split.label(text="")
            col = split.column(align=True)
            
            to_show_items = sorted(sorted(filter(lambda item: item.parent_path == curr_item.path, sn.data_items), key=lambda item: item.type), key=lambda item: item.has_properties, reverse=True)
            for item in to_show_items:
                self.draw_item(sn, col, prev_items+[item])

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn
        
        col = layout.column(align=True)
        for item in sorted(sorted(sn.data_items, key=lambda item: item.type), key=lambda item: item.has_properties, reverse=True):
            if item.parent_path == f"bpy.{sn.data_category}":
                self.draw_item(sn, col, [item])