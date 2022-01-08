import bpy
from .settings import PropertySettings
from ..property_simple import BasicProperty



class SN_SimpleProperty(BasicProperty, bpy.types.PropertyGroup):
    
    expand: bpy.props.BoolProperty(default=True, name="Expand", description="Expand this property")

    def compile(self, context=None):
        sn = bpy.context.scene.sn
        sn.properties[sn.property_index].compile()



class SN_PT_GroupProperty(PropertySettings, bpy.types.PropertyGroup):
    
    type_description = "Group properties can hold multiple other properties.\n" \
                    + "They are used in combination with a pointer or collection property.\n" \
                    + "\n" \
                    + "A common use for group properties is to group your addons settings together."
    
    
    def draw(self, context, layout):
        """ Draws the settings for this property type """
        row = layout.row()
        row.scale_y = 1.2
        row.operator("sn.add_property_item", text="Add Property", icon="ADD")
        
        for prop in self.properties:
            box = layout.box()
            row = box.row()
            subrow = row.row()
            subrow.prop(prop, "expand", text="", icon="DISCLOSURE_TRI_DOWN" if prop.expand else "DISCLOSURE_TRI_RIGHT", emboss=False)
            row.prop(prop, "name", text="")
            row.operator("sn.copy_python_name", text="", icon="COPYDOWN", emboss=False).name = "PROP_PATH_PLACEHOLDER."+prop.python_name

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
        if not len(self.properties):
            code += " "*4 + "pass\n\n"
        code += raw
        return code
    
    
    properties: bpy.props.CollectionProperty(type=SN_SimpleProperty)