import bpy
from ...utils import get_python_name, normalize_code
from ...nodes.base_node import SN_ScriptingBaseNode
from .settings.settings import id_items, property_icons
from .settings.string import SN_PT_StringProperty
from .settings.boolean import SN_PT_BooleanProperty
from .settings.float import SN_PT_FloatProperty
from .settings.integer import SN_PT_IntegerProperty
from .settings.enum import SN_PT_EnumProperty
from .settings.pointer import SN_PT_PointerProperty
from .settings.collection import SN_PT_CollectionProperty
from .settings.group import SN_PT_GroupProperty


# TODO make sure pointers and collections are registered after groups
class SN_PT_GeneralProperties(bpy.types.PropertyGroup):
    
    def draw(self, context, layout):
        """ Draws the general property settings """
        row = layout.row()
        row.prop(self, "property_type")
        row.operator("sn.tooltip", text="", emboss=False, icon="QUESTION").text = self.settings.type_description
        layout.prop(self, "attach_to")
        layout.prop(self, "description")
        
    
    # stores the unregister code for the addon properties with the property as a pointer
    unregister_cache = {}
    
    
    @property
    def data_path(self):
        return f"{self.attach_to.upper()}_PLACEHOLDER.sna_{get_python_name(self.name, 'new_property')}"
    
    @property
    def register_code(self):
        code = f"bpy.types.{self.attach_to}.sna_{get_python_name(self.name, 'new_property')} = bpy.props.{self.settings.prop_type_name}(name='{self.name}', description='{self.description}', {self.settings.register_options})"

        # add enum item function
        # TODO this wont work inside of operators, preferences or on export
        if self.property_type == "Enum":
            code = f"""
                    def sna_enum_items(self, context):
                        for ntree in bpy.data.node_groups:
                            if ntree.bl_idname == "ScriptingNodesTree":
                                for node in ntree.nodes:
                                    if node.bl_idname == "SN_GenerateEnumItemsNode" and node.prop_name == "{self.name}":
                                        return eval(node.code)
                        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
                    {code}
                    """
            code = normalize_code(code)
        return code
    
    @property
    def unregister_code(self):
        return f"del bpy.types.{self.attach_to}.sna_{get_python_name(self.name, 'new_property')}"
    
        
    def compile(self, context=None):
        """ Registers the property and unregisters potential previous version """
        # unregister previous
        if f"{self.as_pointer()}" in self.unregister_cache:
            exec(self.unregister_cache[f"{self.as_pointer()}"])
            del self.unregister_cache[f"{self.as_pointer()}"]
        
        # register
        exec(self.register_code)
        print(f"Serpens Log: Property {self.name} received an update")
        self.unregister_cache[f"{self.as_pointer()}"] = self.unregister_code
        

    def get_name(self):
        return self.get("name", "New Property")  

    def set_name(self, value):
        # TODO make sure name is unique

        # get nodes to update references
        to_update_nodes = []
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                for node in ntree.nodes:
                    if hasattr(node, "prop_name") and node.prop_name == self.name:
                        to_update_nodes.append(node)

        # get properties to update references
        to_update_props = []
        if self.property_type == "Group":
            for prop in bpy.context.scene.sn.properties:
                if prop.property_type == "Pointer" and prop.settings.prop_group == self.name:
                    to_update_props.append(prop)

        # set value
        self["name"] = value

        # update property references
        for prop in to_update_props:
            prop.settings.prop_group = value
        for node in to_update_nodes:
            node.prop_name = value
    
    name: bpy.props.StringProperty(name="Property Name",
                                    description="Name of this property",
                                    default="New Property",
                                    get=get_name,
                                    set=set_name,
                                    update=compile,
                                    subtype="FILE_NAME")
    
    
    description: bpy.props.StringProperty(name="Description",
                                          description="The description of this property, shown in tooltips",
                                          update=compile)
    
    
    @property
    def icon(self):
        return property_icons[self.property_type]
    
    
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


    def get_attach_to_items(self, context):
        items = []
        for item in id_items:
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