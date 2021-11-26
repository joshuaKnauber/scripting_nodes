import bpy


class SN_AddonPreferences(bpy.types.AddonPreferences):

    bl_idname = __name__.partition('.')[0]

    def draw(self, context):
        layout = self.layout


# addon_prefs = context.preferences.addons[bpy.context.scene.sn.addon_tree().sn_graphs[0].short()].preferences
