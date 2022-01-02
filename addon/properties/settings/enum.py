import bpy
from .settings import PropertySettings



class EnumItem(bpy.types.PropertyGroup):
    
    name: bpy.props.StringProperty(name="Name", default="New Item",
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
        row = layout.row()
        row.scale_y = 1.2
        op = row.operator("sn.add_enum_item", text="Add Item", icon="ADD")
        op.item_data_path = "context.scene.sn.properties[context.scene.sn.property_index].settings.items"
        for i, item in enumerate(self.items):
            box = layout.box()
            box.use_property_split = False
            row = box.row()
            row.prop(item, "name")
            op = row.operator("sn.select_icon", icon_value=item.icon, text="Icon" if not item.icon else "", emboss=False)
            op.icon_data_path = f"context.scene.sn.properties[context.scene.sn.property_index].settings.items[{i}]"
            box.prop(item, "description")
        
    
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