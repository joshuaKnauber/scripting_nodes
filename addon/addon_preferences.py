import bpy


class SNA_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__.partition(".")[0]

    def draw(self, context):
        layout = self.layout


# addon_prefs = bpy.context.preferences.addons[__name__.partition('.')[ 0]].preferences
# TODO move to constants
