import bpy


class SN_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__.partition('.')[0]

    show_txt: bpy.props.BoolProperty(name="Show Python File",
                                    description="Shows the python file after compiling the addon",
                                    default=False)
    
    keep_after_error: bpy.props.BoolProperty(name="Keep File After Error",
                                    description="Keeps the python file after an error is encountered",
                                    default=False)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "show_txt")
        layout.prop(self, "keep_after_error")
        
        
        
# addon_prefs = context.preferences.addons[__name__.partition('.')[0]].preferences