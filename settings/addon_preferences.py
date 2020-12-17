import bpy


class SN_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__.partition('.')[0]

    show_txt: bpy.props.BoolProperty(name="Show Python File",
                                    default=False)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "show_txt")
        
        
        
# addon_prefs = context.preferences.addons[__name__.partition('.')[0]].preferences