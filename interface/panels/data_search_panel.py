import bpy
import json
from ...addon.properties.settings.settings import property_icons
        
        
        
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

        row = layout.row()
        row.scale_y = 1.4
        row.operator("sn.reload_data", text="Reload", icon="FILE_REFRESH")
        layout.separator()

        layout.label(text="Source:")
        col = layout.column()
        col.scale_y = 1.4
        col.prop(context.scene.sn, "data_category", expand=True)
        layout.separator()
        
        col = layout.column()
        col.label(text="Filter:")
        row = col.row()
        row.scale_y = 1.2
        row.prop(context.scene.sn, "data_search", text="", icon="VIEWZOOM")
        col.prop(context.scene.sn, "data_filter", expand=True)
        
        
        
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



global_items = { "filter": None, "items": [] }
local_items = { "path": { "filter": None, "items": [] } }
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
            row.scale_y = 0.7

        if curr_item.has_properties:
            row.prop(curr_item, "expand", text="", icon="DISCLOSURE_TRI_DOWN" if curr_item.expand else "DISCLOSURE_TRI_RIGHT", emboss=False)
        else:
            row.label(text="", icon=property_icons[curr_item.type.title()] if curr_item.type.title() in property_icons.keys() else "ERROR")

        subrow = row.row(align=True)
        subrow.alignment = "LEFT"
        parts = list(map(lambda x: x.name.replace("_", " ").title(), prev_items))
        for i, part in enumerate(parts):
            if i < len(parts)-1:
                subcol = subrow.column(align=True)
                subcol.alignment = "LEFT"
                subcol.enabled = False
                subcol.label(text=f"{part} |")
            else:
                subrow.label(text=f"{part}")

        row = row.row()
        row.alignment = "RIGHT"
        
        subrow = row.row()
        subrow.enabled = False
        subrow.label(text=curr_item.type)
        
        row.operator("sn.copy_python_name", text="", icon="COPYDOWN", emboss=False).name = curr_item.path
        if curr_item.has_properties:
            row.context_pointer_set("sn_filter_path", curr_item)
            row.popover("SN_PT_FilterDataSettings", text="", icon="FILTER")
        row.operator("sn.reload_item_data", text="", icon="FILE_REFRESH", emboss=False).path = curr_item.path
        row.operator("sn.tooltip", text="", icon="QUESTION", emboss=False).text = curr_item.description

        if curr_item.expand:
            row = box.row()
            split = row.split(factor=0.025)
            split.label(text="")
            col = split.column(align=True)
            
            filter_key = ""
            if not curr_item.path in local_items or (curr_item.path in local_items and local_items[curr_item.path]["filter"] != filter_key):
                items = filter(lambda item: item.parent_path == curr_item.path, sn.data_items)
                items = sorted(items, key=lambda item: item.type)
                items = list(sorted(items, key=lambda item: item.has_properties, reverse=True))
                local_items[curr_item.path] = {
                    "filter": filter_key,
                    "items": items
                }
                
            for item in local_items[curr_item.path]["items"]:
                if curr_item.data_search in item.name.lower():
                    self.draw_item(sn, col, prev_items+[item])
            if not local_items[curr_item.path]["items"]:
                row = col.row()
                row.enabled = False
                row.label(text="No items found", icon="INFO")

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn
        
        col = layout.column(align=True)
        filter_key = str(sn.data_filter) + sn.data_search
        if global_items["filter"] != filter_key:
            global_items["filter"] = filter_key
            items = sorted(sn.data_items, key=lambda item: item.type)
            items = sorted(items, key=lambda item: item.has_properties, reverse=True)
            global_items["items"] = list(filter(lambda item: item.type in sn.data_filter and sn.data_search in item.name.lower(), items))

        for item in global_items["items"]:
            if item.parent_path == f"bpy.{sn.data_category}":
                self.draw_item(sn, col, [item])