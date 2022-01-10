import bpy
from ...utils import get_python_name
from .settings.settings import property_icons
from .settings.string import SN_PT_StringProperty
from .settings.boolean import SN_PT_BooleanProperty
from .settings.float import SN_PT_FloatProperty
from .settings.integer import SN_PT_IntegerProperty
from .settings.enum import SN_PT_EnumProperty
from .settings.pointer import SN_PT_PointerProperty
from .settings.collection import SN_PT_CollectionProperty



class BasicProperty():
    
    def draw(self, context, layout):
        """ Draws the general property settings """
        row = layout.row()
        row.prop(self, "property_type")
        row.operator("sn.tooltip", text="", emboss=False, icon="QUESTION").text = self.settings.type_description
        layout.prop(self, "description")

    
    @property
    def python_name(self):
        return f"sna_{get_python_name(self.name, 'new_property')}"
    
    
    @property
    def register_code(self):
        code = f"{self.python_name}: bpy.props.{self.settings.prop_type_name}(name='{self.name}', description='{self.description}', {self.settings.register_options})"
        if hasattr(self.settings, "register_code"):
            return self.settings.register_code(code)
        return code
    
    
    @property
    def prop_collection(self):
        """ Returns the collection this property lives in """
        # TODO this might not work with nodes
        path = "[".join(repr(self.path_resolve("name", False)).split("[")[:-1])
        coll = eval(path)
        return coll
    
    
    @property
    def prop_collection_origin(self):
        """ Returns the source where the main property collection lives """
        # TODO this might not work with nodes
        parent_path = repr(self.path_resolve("name", False)).split("properties")[0][:-1]
        parent = eval(parent_path)
        return parent
    
    
    def _compile(self, context=None):
        """ Update the property with the parent classes compile function """
        if hasattr(self, "compile"):
            self.compile(context)
    

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
                                    update=_compile,
                                    subtype="FILE_NAME")
    
    
    description: bpy.props.StringProperty(name="Description",
                                          description="The description of this property, shown in tooltips",
                                          update=_compile)
    
    
    @property
    def icon(self):
        return property_icons[self.property_type]
    
    
    property_type: bpy.props.EnumProperty(name="Type",
                                    description="The type of data this property can store",
                                    update=_compile,
                                    items=[("String", "String", "Stores text, can display a text input or a filepath field", property_icons["String"], 0),
                                           ("Boolean", "Boolean", "Stores True or False, can be used for a checkbox", property_icons["Boolean"], 1),
                                           ("Float", "Float", "Stores a decimal number or a vector", property_icons["Float"], 2),
                                           ("Integer", "Integer", "Stores an integer number or a vector", property_icons["Integer"], 3),
                                           ("Enum", "Enum", "Stores multiple entries to be used as dropdowns", property_icons["Enum"], 4),
                                           ("Pointer", "Pointer", "Stores a reference to certain types of blend data, collection or group properties", property_icons["Pointer"], 5),
                                           ("Collection", "Collection", "Stores a list of certain blend data or property groups to be displayed in lists", property_icons["Collection"], 6)])


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
        }[self.property_type]
    
    stngs_string: bpy.props.PointerProperty(type=SN_PT_StringProperty)
    stngs_boolean: bpy.props.PointerProperty(type=SN_PT_BooleanProperty)
    stngs_float: bpy.props.PointerProperty(type=SN_PT_FloatProperty)
    stngs_integer: bpy.props.PointerProperty(type=SN_PT_IntegerProperty)
    stngs_enum: bpy.props.PointerProperty(type=SN_PT_EnumProperty)
    stngs_pointer: bpy.props.PointerProperty(type=SN_PT_PointerProperty)
    stngs_collection: bpy.props.PointerProperty(type=SN_PT_CollectionProperty)