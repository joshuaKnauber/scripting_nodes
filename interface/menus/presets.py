import bpy


class SN_MT_PresetMenu(bpy.types.Menu):
    bl_idname = "SN_MT_PresetMenu"
    bl_label = "Presets"

    def draw(self, context):
        layout = self.layout
