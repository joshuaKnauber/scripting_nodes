import bpy



class SN_PT_CollectionProperty(bpy.types.PropertyGroup):
    
    type_description = "Integer properties can hold decimal number.\n" \
                    + "They can also be turned into a vector which holds multiple of these.\n" \
                    + "\n" \
                    + "Integers are displayed as number inputs."
    
    
    def draw(self, context, layout, prop):
        """ Draws the settings for this property type """
        
        
    @property
    def prop_type_name(self):
        return "PointerProperty"
    
    
    @property
    def register_options(self):
        return f"type=bpy.types.NodeTree"