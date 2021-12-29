import bpy
from .settings import PropertySettings



class SN_PT_IntegerProperty(PropertySettings, bpy.types.PropertyGroup):
    
    def draw(self, context, layout, prop):
        """ Draws the settings for this property type """
        layout.prop(self, "default")
        layout.separator()
        
        
    @property
    def prop_type_name(self):
        return "IntProperty"
    
    
    @property
    def register_options(self):
        return f"default={self.default}"
    
    
    default: bpy.props.IntProperty(name="Default",
                                    description="Default value of this property (This may not reset automatically for existing attached items)",
                                    update=PropertySettings.compile)