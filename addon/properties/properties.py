import bpy
from ...nodes.compiler import compile_addon
from .property_basic import BasicProperty
from .settings.settings import id_items, id_data, property_icons
from .settings.group import SN_PT_GroupProperty



class FullBasicProperty(BasicProperty):
    
    property_type: bpy.props.EnumProperty(name="Type",
                                    description="The type of data this property can store",
                                    update=BasicProperty.trigger_reference_update,
                                    items=[("String", "String", "Stores text, can display a text input or a filepath field", property_icons["String"], 0),
                                           ("Boolean", "Boolean", "Stores True or False, can be used for a checkbox", property_icons["Boolean"], 1),
                                           ("Float", "Float", "Stores a decimal number or a vector", property_icons["Float"], 2),
                                           ("Integer", "Integer", "Stores an integer number or a vector", property_icons["Integer"], 3),
                                           ("Enum", "Enum", "Stores multiple entries to be used as dropdowns", property_icons["Enum"], 4),
                                           ("Pointer", "Pointer", "Stores a reference to certain types of blend data, collection or group properties", property_icons["Pointer"], 5),
                                           ("Collection", "Collection", "Stores a list of certain blend data or property groups to be displayed in lists", property_icons["Collection"], 6),
                                           ("Group", "Group", "Stores multiple properties to be used in a collection or pointer property", property_icons["Group"], 7)])
    
    @property
    def settings(self):
        return {
            "String": self.stngs_string,
            "Boolean": self.stngs_boolean,
            "Float": self.stngs_float,
            "Integer": self.stngs_integer,
            "Enum": self.stngs_enum,
            "Pointer": self.stngs_pointer,
            "Collection": self.stngs_collection,
            "Group": self.stngs_group,
        }[self.property_type]
    
    
    stngs_group: bpy.props.PointerProperty(type=SN_PT_GroupProperty)



class SN_GeneralProperties(FullBasicProperty, bpy.types.PropertyGroup):
    
    is_scene_prop = True
    
    def draw(self, context, layout):
        """ Draws the general property settings """
        row = layout.row()
        row.prop(self, "property_type")
        row.operator("sn.tooltip", text="", emboss=False, icon="QUESTION").text = self.settings.type_description
        if not self.property_type == "Group":
            layout.prop(self, "attach_to")
            layout.prop(self, "description")
            layout.prop(self, "prop_options")
            
    
    @property
    def data_path(self):
        return f"{self.attach_to.upper()}_PLACEHOLDER.{self.python_name}"
    
    
    @property
    def register_code(self):
        # register non group properties
        if not self.property_type == "Group":
            code = f"bpy.types.{self.attach_to}.{self.python_name} = bpy.props.{self.settings.prop_type_name}(name='{self.name}', description='{self.description}',{self.get_prop_options} {self.settings.register_options})"
        # register group properties
        else:
            code = f"bpy.utils.register_class(SNA_GROUP_{self.python_name})"
        return code
    
    @property
    def unregister_code(self):
        # unregister non group properties
        if not self.property_type == "Group":
            return f"del bpy.types.{self.attach_to}.{self.python_name}"
        # unregister group properties
        else:
            return f"bpy.utils.unregister_class(SNA_GROUP_{self.python_name})"

    @property
    def imperative_code(self):
        if hasattr(self.settings, "imperative_code"):
            return self.settings.imperative_code()
        return ""
    
    
    def compile(self, context=None):
        """ Registers the property and unregisters previous version """
        print(f"Serpens Log: Property {self.name} received an update")
        compile_addon()
        

    def get_attach_to_items(self, context):
        items = []
        for item in id_items:
            items.append((item, item, item))
        return items
    
        
    def get_attach_data(self):
        return id_data[self.attach_to]

    attach_to: bpy.props.EnumProperty(name="Attach To",
                                    description="The type of blend data to attach this property to",
                                    items=get_attach_to_items,
                                    update=FullBasicProperty.trigger_reference_update)