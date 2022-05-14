import bpy
from .settings import PropertySettings



class SN_PT_BooleanProperty(PropertySettings, bpy.types.PropertyGroup):
    
    type_description = "Boolean properties can hold a value of True or False.\n" \
                    + "They can also be turned into a vector which holds multiple of these.\n" \
                    + "\n" \
                    + "Booleans are displayed as checkboxes or toggles in the UI."
    
    def draw(self, context, layout):
        """ Draws the settings for this property type """
        row = layout.row(heading="Default")
        row.enabled = not self.is_vector
        row.prop(self, "default", toggle=True, text=str(self.default))
        layout.separator()
        layout.prop(self, "is_vector")
        col = layout.column()
        col.enabled = self.is_vector
        col.prop(self, "size")
        sub_col = col.column(align=True, heading="Default")
        for i in range(self.size):
            sub_col.prop(self, "vector_default", index=i, text=str(self.vector_default[i]), toggle=True)
        
        
    @property
    def prop_type_name(self):
        if self.is_vector:
            return "BoolVectorProperty"
        return "BoolProperty"
    
    
    @property
    def register_options(self):
        if self.is_vector:
            options = f"size={self.size}, default={tuple(list(self.vector_default)[:self.size])}"
        else:
            options = f"default={self.default}"
        return options + self.update_option
    
    
    default: bpy.props.BoolProperty(name="Default",
                                    description="Default value of this property (This may not reset automatically for existing attached items)",
                                    update=PropertySettings.compile)
    
    def update_vector(self, context):
        self.prop.trigger_reference_update(context)
    
    is_vector: bpy.props.BoolProperty(name="Is Vector",
                                    description="If this property is a vector",
                                    update=update_vector)
    
    size: bpy.props.IntProperty(name="Vector Size", min=2, max=32, default=3,
                                    description="Length of the vector property",
                                    update=PropertySettings.compile)
    
    vector_default: bpy.props.BoolVectorProperty(name="Default",
                                    description="Default value of this property (This may not reset automatically for existing attached items)",
                                    size=32,
                                    update=PropertySettings.compile)