import bpy
from .settings import PropertySettings



class SN_PT_CollectionProperty(PropertySettings, bpy.types.PropertyGroup):
    
    type_description = "Integer properties can hold decimal number.\n" \
                    + "They can also be turned into a vector which holds multiple of these.\n" \
                    + "\n" \
                    + "Integers are displayed as number inputs."
                    
    copy_attributes = ["prop_group"]
    
    
    def draw(self, context, layout):
        """ Draws the settings for this property type """
        src = context.scene.sn
        layout.prop_search(self, "prop_group", src, "properties")
        row = layout.row()
        row.alert = True
        if self.prop_group in src.properties:
            if not src.properties[self.prop_group].property_type == "Group":
                row.label(text="The selected property is not a group!", icon="ERROR")
            elif hasattr(self.prop, "group_prop_parent") and self.prop.group_prop_parent.name == self.prop_group:
                row.label(text="Can't use self reference for this collection!", icon="ERROR")
        else:
            row.label(text="There is no valid property group selected!", icon="ERROR")
        
        
    @property
    def prop_type_name(self):
        return "CollectionProperty"
    
    
    @property
    def register_options(self):
        src = self.prop.prop_collection_origin
        if self.prop_group in src.properties and src.properties[self.prop_group].property_type == "Group":
            if not hasattr(self.prop, "group_prop_parent") or (hasattr(self.prop, "group_prop_parent") and self.prop.group_prop_parent.name != self.prop_group):
                return f"type=SNA_GROUP_{src.properties[self.prop_group].python_name}"
        return "type=bpy.types.PropertyGroup.__subclasses__()[0]"
    
    
    prop_group: bpy.props.StringProperty(name="Property Group",
                                    description="The property group you want to point to",
                                    update=PropertySettings.compile)