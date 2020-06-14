import bpy


class ScriptingNodesAddonPreferences(bpy.types.AddonPreferences):

    bl_idname = __name__.partition('.')[0]

    def draw(self, context):
        layout = self.layout


"""
Access:
addon_prefs = context.preferences.addons[__name__.partition('.')[0]].preferences
"""
