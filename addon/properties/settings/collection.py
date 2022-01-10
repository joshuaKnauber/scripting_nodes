import bpy
from .settings import PropertySettings, id_items



class SN_PT_CollectionProperty(PropertySettings, bpy.types.PropertyGroup):
    
    type_description = "Integer properties can hold decimal number.\n" \
                    + "They can also be turned into a vector which holds multiple of these.\n" \
                    + "\n" \
                    + "Integers are displayed as number inputs."
    
    
    def draw(self, context, layout):
        """ Draws the settings for this property type """
        src = self.prop.prop_collection_origin
        layout.prop_search(self, "prop_group", src, "properties")
        row = layout.row()
        row.alert = True
        if self.prop_group in src.properties:
            if not src.properties[self.prop_group].property_type == "Group":
                row.label(text="The selected property is not a group!", icon="ERROR")
        else:
            row.label(text="There is no valid property group selected!", icon="ERROR")
        
        
    @property
    def prop_type_name(self):
        return "CollectionProperty"
    
    
    @property
    def register_options(self):
        src = self.prop.prop_collection_origin
        if self.prop_group in src.properties and src.properties[self.prop_group].property_type == "Group":
            return f"type=SNA_GROUP_{src.properties[self.prop_group].python_name}"
        else:
            return "type=None" # TODO replace this with always existing group
    
    
    prop_group: bpy.props.StringProperty(name="Property Group",
                                    description="The property group you want to point to",
                                    update=PropertySettings.compile)