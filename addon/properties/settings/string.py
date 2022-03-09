import bpy
from .settings import PropertySettings



class SN_PT_StringProperty(PropertySettings, bpy.types.PropertyGroup):
    
    type_description = "String properties can hold a line of text.\n" \
                    + "\n" \
                    + "String properties are displayed as text inputs in the UI. \n" \
                    + "There are subtypes to add a file selector to the string property."

    
    def draw(self, context, layout):
        """ Draws the settings for this property type """
        layout.prop(self, "subtype")
        layout.prop(self, "default")
        layout.separator()
        layout.prop(self, "maxlen")
        
    
    @property
    def prop_type_name(self):
        return "StringProperty"
    
    
    @property
    def register_options(self):
        return f"default='{self.default}', subtype='{self.subtype}', maxlen={self.maxlen}{self.update_option}"
    
    
    default: bpy.props.StringProperty(name="Default",
                                    description="Default value of this property (This may not reset automatically for existing attached items)",
                                    update=PropertySettings.compile)

    
    subtype: bpy.props.EnumProperty(name="Subtype",
                                    description="The subtype of this property. This changes how the property is displayed",
                                    update=PropertySettings.compile,
                                    items=[("NONE", "None", "No subtype, just a default string input"),
                                           ("FILE_PATH", "File Path", "Display this property as a file path"),
                                           ("DIR_PATH", "Directory Path", "Display this property as a directory path"),
                                        #    ("FILE_NAME", "File Name", "Display that property as a file name"),
                                           ("BYTE_STRING", "Byte String", "Stores the string as a UTF-8 encoded byte string"),
                                           ("PASSWORD", "Password", "Displays asterisks in the UI to hide the typed string")])
    
    
    maxlen: bpy.props.IntProperty(name="Max Length",
                                  description="The maximum length of the string (0 is unlimited)",
                                  min=0,
                                  default=0,
                                  update=PropertySettings.compile)