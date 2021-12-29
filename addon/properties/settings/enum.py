import bpy
from .settings import PropertySettings



class EnumItem(bpy.types.PropertyGroup):
    
    name: bpy.props.StringProperty(name="Name",
                                description="Name of this enum item")
    
    description: bpy.props.StringProperty(name="Description",
                                description="Description of this enum item")
    
    icon: bpy.props.IntProperty(name="Icon", default=0, min=0,
                                description="Icon value of this enum item")




class SN_PT_EnumProperty(PropertySettings, bpy.types.PropertyGroup):
    
    def draw(self, context, layout, prop):
        """ Draws the settings for this property type """
        layout.prop(self, "enum_flag")
        layout.separator()
        for item in self.items:
            box = layout.box()
            box.prop(item, "name")
            box.prop(item, "description", text="")
        
    
    @property
    def prop_type_name(self):
        return "EnumProperty"
    
    
    @property
    def register_options(self):
        options = "items=[]"
        if self.enum_flag:
            options += ", options={'ENUM_FLAG'}"
        return options
    
    
    enum_flag: bpy.props.BoolProperty(name="Select Multiple",
                                description="Lets you select multiple options from this property",
                                update=PropertySettings.compile)
    
    
    items: bpy.props.CollectionProperty(type=EnumItem,
                                name="Items",
                                description="Enum Items")