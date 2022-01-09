import bpy
from .settings import PropertySettings, id_items



class SN_PT_PointerProperty(PropertySettings, bpy.types.PropertyGroup):
    
    type_description = "Pointer properties can point to specific types of blend data or property groups.\n" \
                    + "\n" \
                    + "They are often used to point to your addons settings, which could live grouped\n" \
                    + "in a property group and be attached to the scene.\n" \
                    + "\n" \
                    + "When used with blend data, you can use pointers to let the user select the data\n" \
                    + "from a dropdown and get the blend data from the property."
    
    
    def draw(self, context, layout):
        """ Draws the settings for this property type """
        if getattr(self.prop, "is_scene_prop", False):
            layout.prop(self, "use_prop_group")
        if not self.use_prop_group:
            layout.prop(self, "data_type")
        else:
            layout.prop_search(self, "prop_group", context.scene.sn, "properties")
            row = layout.row()
            row.alert = True
            if self.prop_group and self.prop_group in context.scene.sn.properties:
                if not context.scene.sn.properties[self.prop_group].property_type == "Group":
                    row.label(text="The selected property is not a group!", icon="ERROR")
            else:
                row.label(text="There is no valid property group selected!", icon="ERROR")
        
        
    @property
    def prop_type_name(self):
        return "PointerProperty"
    
    
    @property
    def register_options(self):
        if not self.use_prop_group:
            data_type = "bpy.types."+self.data_type
        else:
            sn = bpy.context.scene.sn
            if self.prop_group in sn.properties and sn.properties[self.prop_group].property_type == "Group":
                data_type = f"SNA_GROUP_{bpy.context.scene.sn.properties[self.prop_group].python_name}"
            else:
                data_type = "bpy.types.Scene"
        return f"type={data_type}"
    
    
    def get_data_items(self, context):
        items = []
        for item in id_items:
            items.append((item, item, item))
        return items

    data_type: bpy.props.EnumProperty(name="Data Type",
                                    description="The type of blend data to have this property point to",
                                    items=get_data_items,
                                    update=PropertySettings.compile)
    
    
    use_prop_group: bpy.props.BoolProperty(name="Use Property Group",
                                    description="Point to a custom property group you created",
                                    update=PropertySettings.compile)
    
    
    prop_group: bpy.props.StringProperty(name="Property Group",
                                    description="The property group you want to point to",
                                    update=PropertySettings.compile)