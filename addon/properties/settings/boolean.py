import bpy
from .settings import PropertySettings



class SN_PT_BooleanProperty(PropertySettings, bpy.types.PropertyGroup):
    
    def draw(self, context, layout, prop):
        """ Draws the settings for this property type """
        layout.prop(self, "default")
        layout.separator()
        layout.prop(self, "is_vector")
        col = layout.column()
        col.enabled = self.is_vector
        col.prop(self, "size")
        
        
    @property
    def prop_type_name(self):
        if self.is_vector:
            return "BoolVectorProperty"
        return "BoolProperty"
    
    
    @property
    def register_options(self):
        return f"default={self.default}"
    
    
    default: bpy.props.BoolProperty(name="Default",
                                    description="Default value of this property (This may not reset automatically for existing attached items)",
                                    update=PropertySettings.compile)
    
    
    is_vector: bpy.props.BoolProperty(name="Is Vector",
                                    description="If this property is a vector",
                                    update=PropertySettings.compile)
    
    size: bpy.props.IntProperty(name="Vector Size", min=2, max=32, default=3,
                                    description="Length of the vector property",
                                    update=PropertySettings.compile)