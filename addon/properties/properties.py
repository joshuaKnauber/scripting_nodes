import bpy
from ...utils import print_debug_code
from .property_basic import BasicProperty
from .property_ops import get_sorted_props
from .settings.settings import id_items, property_icons
from .settings.group import SN_PT_GroupProperty



class FullBasicProperty(BasicProperty):
    
    property_type: bpy.props.EnumProperty(name="Type",
                                    description="The type of data this property can store",
                                    update=BasicProperty._compile,
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
        
    
    # stores the unregister code for the addon properties with the property as a pointer
    unregister_cache = {}
    
    
    @property
    def data_path(self):
        return f"{self.attach_to.upper()}_PLACEHOLDER.{self.python_name}"
    
    
    @property
    def register_code(self):
        # register non group properties
        if not self.property_type == "Group":
            code = f"bpy.types.{self.attach_to}.{self.python_name} = bpy.props.{self.settings.prop_type_name}(name='{self.name}', description='{self.description}', {self.settings.register_options})"
        # register group properties
        else:
            code = f"bpy.utils.register_class(SNA_GROUP_{self.python_name})"
            if not bpy.context.scene.sn.is_exporting:
                code += f"\nbpy.context.scene.sn.unregister_cache['{self.as_pointer()}'] = SNA_GROUP_{self.python_name}"
        # add register code from prop settings
        if hasattr(self.settings, "register_code"):
            return self.settings.register_code(code)
        return code
    
    @property
    def unregister_code(self):
        # unregister non group properties
        if not self.property_type == "Group":
            return f"del bpy.types.{self.attach_to}.{self.python_name}"
        # unregister group properties
        else:
            if bpy.context.scene.sn.is_exporting:
                return f"bpy.utils.unregister_class(SNA_GROUP_{self.python_name})"
            else:
                code = f"bpy.utils.unregister_class(bpy.context.scene.sn.unregister_cache['{self.as_pointer()}'])\n"
                code += f"del bpy.context.scene.sn.unregister_cache['{self.as_pointer()}']"
                return code
    

    def unregister_all(self):
        """ Unregisters all scene properties """
        if "properties" in bpy.context.scene.sn.unregister_cache:
            try: bpy.context.scene.sn.unregister_cache["properties"]()
            except Exception as err:
                print("Serpens Log: Failed to unregister properties. Restart blender to clean the file!")
                print(err)
            del bpy.context.scene.sn.unregister_cache["properties"]
        

    def register_all(self):
        """ Registers all scene properties """
        props = get_sorted_props(bpy.context.scene.sn.properties.values())

        # get register code
        reg_code = "def register():\n"
        for prop in props:
            for line in prop.register_code.split("\n"):
                reg_code += " "*4 + line + "\n"
        
        # get unregister code
        unreg_code = "\ndef unregister():\n"
        props.reverse()
        for prop in props:
            for line in prop.unregister_code.split("\n"):
                unreg_code += " "*4 + line + "\n"
        
        store_unregister = f"bpy.context.scene.sn.unregister_cache['properties'] = unregister\n"
        assembled = "import bpy\n\n" + reg_code + unreg_code + "\nregister()\n" + store_unregister

        # register
        print_debug_code(assembled)
        try: exec(assembled)
        except Exception as err:
            print("Serpens Log: Failed to register properties. Restart blender to clean the file!")
            print(err)
    
    
    def compile(self, context=None):
        """ Registers the property and unregisters previous version """
        # unregister previous
        self.unregister_all()
        # register
        self.register_all()
        print(f"Serpens Log: Property {self.name} received an update")
        

    def get_attach_to_items(self, context):
        items = []
        for item in id_items:
            items.append((item, item, item))
        return items

    attach_to: bpy.props.EnumProperty(name="Attach To",
                                    description="The type of blend data to attach this property to",
                                    items=get_attach_to_items,
                                    update=compile)