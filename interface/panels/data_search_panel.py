import bpy


class SN_PT_navigation_bar(bpy.types.Panel):
    bl_label = "Preferences Navigation"
    bl_space_type = "PREFERENCES"
    bl_region_type = "NAVIGATION_BAR"
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn


class SN_PT_FilterDataSettings(bpy.types.Panel):
    bl_idname = "SN_PT_FilterDataSettings"
    bl_label = "Filter"
    bl_space_type = "PREFERENCES"
    bl_region_type = "WINDOW"
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        layout = self.layout


class SN_PT_data_search(bpy.types.Panel):
    bl_space_type = "PREFERENCES"
    bl_region_type = "WINDOW"
    bl_label = "Display"
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn
