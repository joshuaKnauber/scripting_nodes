import bpy
from ...addon.properties.settings.settings import property_icons
from ...settings.data_properties import filter_defaults
        
        
        
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

        row = layout.row()
        row.scale_y = 1.4
        row.alert = True
        row.operator("sn.exit_search", text="Exit", icon="PANEL_CLOSE")
        layout.separator()

        layout.operator("wm.url_open", text="How to", icon="QUESTION").url = "https://joshuaknauber.notion.site/Blend-Data-33e9f2ea40f44c2498cb26838662b621"

        layout.separator()
        layout.label(text="Source:")
        col = layout.column()
        col.scale_y = 1.4
        col.prop(context.scene.sn, "data_category", expand=True)
        layout.separator()

        col = layout.column(align=True)
        row = col.row()
        row.scale_y = 1.4
        row.operator("sn.reload_data", text="Reload", icon="FILE_REFRESH")
        if context.scene.sn.data_category == "context":
            box = col.box()
            if context.scene.sn.copied_context:
                copied = context.scene.sn.copied_context[0]
                col = box.column(align=True)
                col.label(text=f"Reload Context:")
                subrow = col.row()
                subrow.enabled = False
                subrow.label(text=f"{copied['area'].type.replace('_', ' ').title()} {copied['region'].type.replace('_', ' ').title()}")
            else:
                box.label(text="No context copied!")

        layout.separator()
        col = layout.column()
        col.label(text="Filter Overview:")
        row = col.row()
        row.scale_y = 1.2
        row.prop(context.scene.sn, "data_search", text="", icon="VIEWZOOM")
        col.prop(context.scene.sn, "data_filter", expand=True)
        
        layout.separator()
        layout.prop(context.scene.sn, "show_path")
        
        
        
class SN_PT_FilterDataSettings(bpy.types.Panel):
    bl_idname = "SN_PT_FilterDataSettings"
    bl_label = "Filter"
    bl_space_type = "PREFERENCES"
    bl_region_type = "WINDOW"
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        layout = self.layout
        if getattr(context, "sn_filter_path", None):
            layout.prop(context.sn_filter_path, "data_search", text="", icon="VIEWZOOM")
            col = layout.column()
            col.prop(context.sn_filter_path, "data_filter")



path_notes = {
    "bpy.context.preferences.keymap": "Copy shortcuts from Context -> Window Manager -> Keyconfigs -> Your Shortcut -> Type",
    "bpy.context.window_manager.keyconfigs": "To display a shortcut, find it in a Key Config below, copy its Type property and check Full Shortcut on the node",
}

class SN_PT_data_search(bpy.types.Panel):
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_label = "Display"
    bl_options = {'HIDE_HEADER'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.sn.hide_preferences
    
    def should_draw(self, item, search_value, filters):
        if search_value.lower() in item["name"].lower():
            return item["type"] in filters
        return False
    
    def draw_item(self, layout, item):
        box = layout.box()
        row = box.row()
        
        if not item["has_properties"]:
            row.scale_y = 0.75
        else:
            op = row.operator("sn.expand_data", text="", icon="TRIA_DOWN" if item["expanded"] else "TRIA_RIGHT", emboss=False)
            op.path = item["path"]

            has_filters = item["data_search"] != "" or item["data_filter"] != filter_defaults
            op = row.operator("sn.filter_data", text="", icon="FILTER", emboss=has_filters, depress=has_filters)
            op.path = item["path"]

        row.label(text=item["name"])
        
        icon = property_icons[item["type"]] if item["type"] in property_icons else "ERROR"
        subrow = row.row()
        subrow.enabled = False
        subrow.label(text=item["type"], icon=icon)

        if bpy.context.scene.sn.show_path:
            subrow = row.row()
            subrow.enabled = False
            subrow.label(text=item["path"])
        
        if item["has_properties"]:
            op = row.operator("sn.reload_item_data", text="", icon="FILE_REFRESH", emboss=False)
            op.path = item["path"]

        op = row.operator("sn.copy_data_path", text="", icon="COPYDOWN", emboss=False)
        op.path = item["path"]
        op.type = item["type"]
        
        if item["expanded"]:
            row = box.row()
            split = row.split(factor=0.015)
            split.label(text="")
            col = split.column(align=True)
                
            if item["path"] in path_notes:
                box = col.box()
                box.scale_y = 0.75
                box.label(text=path_notes[item["path"]], icon="INFO")
            
            is_empty = True
            for key in item["properties"].keys():
                sub_item = item["properties"][key]
                if self.should_draw(sub_item, item["data_search"], item["data_filter"]):
                    self.draw_item(col, sub_item)
                    if sub_item["clamped"]:
                        box = col.box()
                        box.scale_y = 0.75
                        box.label(text="... Shortened because of too many items", icon="PLUS")
                        col.separator()
                    is_empty = False

            if is_empty:
                col.label(text="No Items for these filters!", icon="INFO")

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn
        
        col = layout.column(align=True)
        is_empty = True
        for key in sn.data_items[sn.data_category].keys():
            item = sn.data_items[sn.data_category][key]
            if self.should_draw(item, sn.data_search, sn.data_filter):
                self.draw_item(col, item)
                is_empty = False
                
        if is_empty:
            layout.label(text="No Items for these filters!", icon="INFO")