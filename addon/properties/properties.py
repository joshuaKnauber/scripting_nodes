import bpy
from ...utils import get_python_name
from .settings.string import SN_PT_StringProperty
from .settings.boolean import SN_PT_BooleanProperty
from .settings.float import SN_PT_FloatProperty
from .settings.integer import SN_PT_IntegerProperty
from .settings.enum import SN_PT_EnumProperty
from .settings.pointer import SN_PT_PointerProperty
from .settings.collection import SN_PT_CollectionProperty
from .settings.group import SN_PT_GroupProperty



class SN_PT_GeneralProperties(bpy.types.PropertyGroup):
    
    def draw(self, context, layout):
        """ Draws the general property settings """
        layout.prop(self, "property_type")
        layout.prop(self, "attach_to")
        layout.prop(self, "description")
        
    
    # stores the unregister code for the addon properties with the property as a pointer
    unregister_cache = {}
    
    
    @property
    def register_code(self):
        return f"bpy.types.{self.attach_to}.{get_python_name(self.name, 'new_property')} = bpy.props.{self.settings.prop_type_name}(name='{self.name}', description='{self.description}', {self.settings.register_options})"
    
    @property
    def unregister_code(self):
        return f"del bpy.types.{self.attach_to}.{get_python_name(self.name, 'new_property')}"
    
        
    def compile(self, context=None):
        """ Registers the property and unregisters potential previous version """
        # unregister previous
        if f"{self.as_pointer()}" in self.unregister_cache:
            exec(self.unregister_cache[f"{self.as_pointer()}"])
            del self.unregister_cache[f"{self.as_pointer()}"]
        
        # register
        exec(self.register_code)
        self.unregister_cache[f"{self.as_pointer()}"] = self.unregister_code
        

    def get_name(self):
        return self.get("name", "New Property")  

    def set_name(self, value):
        # TODO make sure name is unique
        # NOTE maybe check for references here when name changes to update them
        self["name"] = value
    
    name: bpy.props.StringProperty(name="Property Name",
                                    description="Name of this property",
                                    default="New Property",
                                    get=get_name,
                                    set=set_name,
                                    update=compile)
    
    
    description: bpy.props.StringProperty(name="Description",
                                          description="The description of this property, shown in tooltips",
                                          update=compile)
    
    
    property_icons = {
        "String": "SYNTAX_OFF",
        "Boolean": "FORCE_CHARGE",
        "Float": "CON_TRANSLIKE",
        "Integer": "DRIVER_TRANSFORM",
        "Enum": "PRESET",
        "Pointer": "MONKEY",
        "Collection": "ASSET_MANAGER",
        "Group": "FILEBROWSER",
    }
    
    @property
    def icon(self):
        return self.property_icons[self.property_type]
    
    
    property_type: bpy.props.EnumProperty(name="Type",
                                    description="The type of data this property can store",
                                    update=compile,
                                    items=[("String", "String", "Stores text, can display a text input or a filepath field", property_icons["String"], 0),
                                           ("Boolean", "Boolean", "Stores True or False, can be used for a checkbox", property_icons["Boolean"], 1),
                                           ("Float", "Float", "Stores a decimal number or a vector", property_icons["Float"], 2),
                                           ("Integer", "Integer", "Stores an integer number or a vector", property_icons["Integer"], 3),
                                           ("Enum", "Enum", "Stores multiple entries to be used as dropdowns", property_icons["Enum"], 4),
                                           ("Pointer", "Pointer", "Stores a reference to certain types of blend data, collection or group properties", property_icons["Pointer"], 5),
                                           ("Collection", "Collection", "Stores a list of certain blend data or property groups to be displayed in lists", property_icons["Collection"], 6),
                                           ("Group", "Group", "Stores multiple properties to be used in a collection or pointer property", property_icons["Group"], 7)])


    id_data = ["Scene", "Action", "Armature", "Brush", "CacheFile", "Camera",
        "Collection", "Curve", "FreestyleLineStyle", "GreasePencil",
        "Image", "Key", "Lattice", "Library", "Light", "LightProbe",
        "Mask", "Material", "Mesh", "MetaBall", "MovieClip", "NodeTree",
        "Object", "PaintCurve", "Palette", "ParticleSettings",
        "Screen", "Sound", "Speaker", "Text", "Texture", "VectorFont",
        "Volume", "WindowManager", "WorkSpace", "World"]


    def get_attach_to_items(self, context):
        items = []
        for item in self.id_data:
            items.append((item, item, item))
        return items

    attach_to: bpy.props.EnumProperty(name="Attach To",
                                    description="The type of blend data to attach this property to",
                                    items=get_attach_to_items,
                                    update=compile)


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
    
    stngs_string: bpy.props.PointerProperty(type=SN_PT_StringProperty)
    stngs_boolean: bpy.props.PointerProperty(type=SN_PT_BooleanProperty)
    stngs_float: bpy.props.PointerProperty(type=SN_PT_FloatProperty)
    stngs_integer: bpy.props.PointerProperty(type=SN_PT_IntegerProperty)
    stngs_enum: bpy.props.PointerProperty(type=SN_PT_EnumProperty)
    stngs_pointer: bpy.props.PointerProperty(type=SN_PT_PointerProperty)
    stngs_collection: bpy.props.PointerProperty(type=SN_PT_CollectionProperty)
    stngs_group: bpy.props.PointerProperty(type=SN_PT_GroupProperty)