import bpy



class SN_PT_GroupProperty(bpy.types.PropertyGroup):
    
    type_description = "Boolean properties can hold a value of True or False.\n" \
                    + "They can also be turned into a vector which holds multiple of these.\n" \
                    + "\n" \
                    + "Booleans are displayed as checkboxes or toggles in the UI."
    
    
    def draw(self, context, layout, prop):
        """ Draws the settings for this property type """
        
        
    @property
    def prop_type_name(self):
        return "PointerProperty"
    
    
    @property
    def register_options(self):
        return f"type=bpy.types.NodeTree"