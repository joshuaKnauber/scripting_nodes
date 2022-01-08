import bpy
from ....utils import normalize_code
from .settings import PropertySettings
from ..property_simple import BasicProperty



class SN_SimpleProperty(BasicProperty, bpy.types.PropertyGroup):
    
    expand: bpy.props.BoolProperty(default=True, name="Expand", description="Expand this property")



class SN_PT_GroupProperty(PropertySettings, bpy.types.PropertyGroup):
    
    type_description = "Boolean properties can hold a value of True or False.\n" \
                    + "They can also be turned into a vector which holds multiple of these.\n" \
                    + "\n" \
                    + "Booleans are displayed as checkboxes or toggles in the UI."
    
    
    def draw(self, context, layout):
        """ Draws the settings for this property type """
        row = layout.row()
        row.scale_y = 1.2
        row.operator("sn.add_property_item", text="Add Property", icon="ADD")
        
        for prop in self.properties:
            box = layout.box()
            row = box.row()
            row.prop(prop, "expand", text="", emboss=False, icon="DISCLOSURE_TRI_DOWN" if prop.expand else "DISCLOSURE_TRI_RIGHT")
            row.prop(prop, "name", text="")

            if prop.expand:
                prop.draw(context, box)
                box.separator()
                prop.settings.draw(context, box)
        
        
    @property
    def prop_type_name(self):
        return "PointerProperty"
    
    
    @property
    def register_options(self):
        return f"type=bpy.types.NodeTree"
    
    
    def register_code(self, raw):
        code = f"class SNA_GROUP_{self.prop.python_name}(bpy.types.PropertyGroup):\n\n"
        for prop in self.properties:
            code += " "*4 + prop.register_code + "\n\n"
        code += raw
        return code
    
    
    properties: bpy.props.CollectionProperty(type=SN_SimpleProperty)