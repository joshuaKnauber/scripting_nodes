from unittest import result
import bpy
from bl_ui import space_userpref
import threading

from . import scraper


class SNA_OT_Scrape(bpy.types.Operator):
    bl_idname = "sna.scrape"
    bl_label = "Scrape"
    bl_description = "Scrape and store the current blender data for searching"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        thread = threading.Thread(target=scraper.store_blender_data)
        thread.start()
        return {"FINISHED"}


class SNA_OT_LaunchBrowser(bpy.types.Operator):
    bl_idname = "sna.launch_browser"
    bl_label = "Launch Blend Data Browser"
    bl_description = "Launches the blend data browser"
    bl_options = {"REGISTER", "INTERNAL"}

    def hide_preference_ui(self, context):
        sna = context.scene.sna
        for cls in space_userpref.classes:
            try:
                if sna.show_bd_browser:
                    bpy.utils.unregister_class(cls)
                else:
                    bpy.utils.register_class(cls)
            except:
                pass

    def open_preferences(self, context):
        for area in context.screen.areas:
            if area.type == "PREFERENCES":
                break
        else:
            bpy.ops.screen.userpref_show("INVOKE_DEFAULT")

    def execute(self, context):
        context.scene.sna.show_bd_browser = True
        self.open_preferences(context)
        self.hide_preference_ui(context)
        return {"FINISHED"}


class SNA_OT_SelectResults(bpy.types.Operator):
    bl_idname = "sna.select_result"
    bl_label = "Select Result"
    bl_description = "Select this result"
    bl_options = {"REGISTER", "INTERNAL"}

    key: bpy.props.StringProperty()

    def execute(self, context):
        bpy.context.scene.sna.blend_data_selected_result = self.key
        return {"FINISHED"}


class SNA_OT_DeselectResults(bpy.types.Operator):
    bl_idname = "sna.deselect_result"
    bl_label = "Deselect Result"
    bl_description = "Deselect the current result"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        bpy.context.scene.sna.blend_data_selected_result = ""
        return {"FINISHED"}
