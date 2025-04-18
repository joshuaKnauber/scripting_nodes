import bpy
from ...utils import get_python_name, unique_collection_name
from .settings.settings import property_icons
from .settings.string import SN_PT_StringProperty
from .settings.boolean import SN_PT_BooleanProperty
from .settings.float import SN_PT_FloatProperty
from .settings.integer import SN_PT_IntegerProperty
from .settings.enum import SN_PT_EnumProperty
from .settings.pointer import SN_PT_PointerProperty
from .settings.collection import SN_PT_CollectionProperty


_prop_collection_cache = {} # stores key, value of prop.as_pointer, prop collection
_prop_origin_cache = {} # stores key, value of prop.as_pointer, prop collection origin

class BasicProperty():
    
    def draw(self, context, layout):
        """ Draws the general property settings """
        row = layout.row()
        row.prop(self, "property_type")
        row.operator("sn.tooltip", text="", emboss=False, icon="QUESTION").text = self.settings.type_description
        layout.prop(self, "description")
        
        col = layout.column(align=True)
        col.prop_enum(self, "prop_options", "HIDDEN", text="Hidden")
        col.prop_enum(self, "prop_options", "SKIP_SAVE", text="Skip Save")
        if self.property_type in {"Float", "Integer", "Boolean"}:
            col.prop_enum(self, "prop_options", "ANIMATABLE", text="Animatable")
        if self.property_type == "String":
            col.prop_enum(self, "prop_options", "TEXTEDIT_UPDATE", text="Textedit Update")

    
    # cache python names so they only have to be generated once
    cached_python_names = {}
    cached_python_name: bpy.props.StringProperty()
    cached_human_name: bpy.props.StringProperty()
    
    @property
    def python_name(self):
        if self.name == self.cached_human_name and self.cached_python_name: return self.cached_python_name
        if self.name in self.cached_python_names: return self.cached_python_names[self.name]

        names = []
        for prop in self.prop_collection:
            if prop == self:
                break
            names.append(prop.python_name)
        
        name = unique_collection_name(f"sna_{get_python_name(self.name, 'new_property')}", "new_property", names, "_")
        try:
            self.cached_python_name = name
            self.cached_human_name = self.name
        except AttributeError: pass
        self.cached_python_names[self.name] = name
        return name
    
    
    @property
    def get_prop_options(self):
        options = ""
        if self.prop_options:
            options = " options={" + ", ".join(map(lambda option: f"'{option}'", list(self.prop_options))) + "},"
        return options
    
    
    @property
    def register_code(self):         
        code = f"{self.python_name}: bpy.props.{self.settings.prop_type_name}(name='{self.name}', description='{self.description}',{self.get_prop_options} {self.settings.register_options})"
        if hasattr(self.settings, "register_code"):
            return self.settings.register_code(code)
        return code
    
    
    @property
    def prop_collection(self):
        """ Returns the collection this property lives in """
        if self.id_data.bl_rna.identifier == "ScriptingNodesTree":
            # find property in nodes to return
            if not str(self.as_pointer()) in _prop_collection_cache:
                for node in self.id_data.nodes:
                    if hasattr(node, "properties"):
                        for prop in node.properties:
                            if prop == self:
                                _prop_collection_cache[str(self.as_pointer())] = node.properties
                                break
                            elif prop.property_type == "Group":
                                for subprop in prop.settings.properties:
                                    if subprop == self:
                                        _prop_collection_cache[str(self.as_pointer())] = prop.settings.properties
                                        break
            return _prop_collection_cache[str(self.as_pointer())]
        
        else:
            path = "[".join(repr(self.path_resolve("name", False)).split("[")[:-1])
            if path.endswith("scenes"):
                path = "bpy.context.scene.sn.properties"
            coll = eval(path)
            return coll
    
    
    @property
    def prop_collection_origin(self):
        """ Returns the source where the main property collection lives """
        if self.id_data.bl_rna.identifier == "ScriptingNodesTree":
            # find property in nodes to return
            if not str(self.as_pointer()) in _prop_origin_cache:
                for node in self.id_data.nodes:
                    if hasattr(node, "properties"):
                        for prop in node.properties:
                            if prop == self:
                                _prop_origin_cache[str(self.as_pointer())] = node
                                break
                            elif prop.property_type == "Group":
                                for subprop in prop.settings.properties:
                                    if subprop == self:
                                        _prop_origin_cache[str(self.as_pointer())] = node
                                        break
            return _prop_origin_cache[str(self.as_pointer())]
        
        else:
            parent_path = repr(self.path_resolve("name", False)).split("properties")[0][:-1]
            parent = eval(parent_path)
            return parent
        

    @property
    def full_prop_path(self):
        """ Returns the full data path for this property """
        main_prop_path = f"{repr(self.prop_collection_origin)}.properties"
        if hasattr(self, "group_prop_parent"):
            main_prop_path += f"['{self.group_prop_parent.name}'].settings.properties"
        main_prop_path += f"['{self.name}']"
        return main_prop_path
    
    
    def _compile(self, context=None):
        """ Update the property with the parent classes compile function """
        if hasattr(self, "compile"):
            self.compile(context)
    

    def get_name(self):
        return self.get("name", "Prop Default")

    def get_unique_name(self, value):
        names = list(map(lambda item: item.name, list(filter(lambda item: item!=self, self.prop_collection))))
        return unique_collection_name(value, "New Property", names, " ")

    def set_name(self, value):
        value = self.get_unique_name(value)

        # get nodes to update references
        to_update_nodes = []
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                for node in ntree.nodes:
                    if getattr(node, "prop_name", None) == self.name or getattr(node, "prop_group", None) == self.name:
                        if self.property_type == "Group":
                            if hasattr(node, "get_prop_source") and node.get_prop_source() == self.settings:
                                to_update_nodes.append((node, "prop_group"))
                        else:
                            if hasattr(node, "get_prop_source") and node.get_prop_source() and node.get_prop_source().properties == self.prop_collection and self.name in node.get_prop_source().properties:
                                to_update_nodes.append((node, "prop_name"))

        # get properties to update references
        to_update_props = []
        if self.property_type == "Group":
            for prop in self.prop_collection:
                if prop.property_type in ["Pointer", "Collection"] and prop.settings.prop_group == self.name:
                    to_update_props.append(prop)
                elif prop.property_type == "Group" and prop != self:
                    for subprop in prop.settings.properties:
                        if subprop.property_type in ["Pointer", "Collection"] and subprop.settings.prop_group == self.name:
                            to_update_props.append(subprop)

        # set value
        self["name"] = value

        # update property references
        for prop in to_update_props:
            prop.settings.prop_group = value
        for node, key in to_update_nodes:
            setattr(node, key, value)
    
    name: bpy.props.StringProperty(name="Property Name",
                                    description="Name of this property",
                                    default="Prop Default",
                                    get=get_name,
                                    set=set_name,
                                    update=_compile)
    
    
    description: bpy.props.StringProperty(name="Description",
                                          description="The description of this property, shown in tooltips",
                                          update=_compile)
    
    
    @property
    def icon(self):
        return property_icons[self.property_type]
    
    
    def trigger_reference_update(self, context):
        # get nodes to update references
        to_update_nodes = []
        key = "prop_group" if self.property_type == "Group" else "prop_name"
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                for node in ntree.nodes:
                    if hasattr(node, key) and getattr(node, key) == self.name:
                        to_update_nodes.append((node, key))
                            
        for node, key in to_update_nodes:
            # trigger an update on the affected nodes
            setattr(node, key, self.name)
        self._compile()

    
    def get_types(self, context):
        items = [("String", "String", "Stores text, can display a text input or a filepath field", property_icons["String"], 0),
            ("Boolean", "Boolean", "Stores True or False, can be used for a checkbox", property_icons["Boolean"], 1),
            ("Float", "Float", "Stores a decimal number or a vector", property_icons["Float"], 2),
            ("Integer", "Integer", "Stores an integer number or a vector", property_icons["Integer"], 3),
            ("Enum", "Enum", "Stores multiple entries to be used as dropdowns", property_icons["Enum"], 4),
            ("Pointer", "Pointer", "Stores a reference to certain types of blend data, collection or group properties", property_icons["Pointer"], 5),
            ("Collection", "Collection", "Stores a list of certain blend data or property groups to be displayed in lists", property_icons["Collection"], 6)]
        if not self.allow_pointers:
            items.pop(5)
        return items
        
    property_type: bpy.props.EnumProperty(name="Type",
                                    description="The type of data this property can store",
                                    update=trigger_reference_update,
                                    items=get_types)

    allow_pointers: bpy.props.BoolProperty(default=True)


    def get_prop_option_items(self, context):
        items = [("HIDDEN", "Hidden", "Hide property from operator popups"),
                ("SKIP_SAVE", "Skip Save", "Don't save this property between calls"),
                ("ANIMATABLE", "Animatable", "Enable if this property should be animatable"),
                ("TEXTEDIT_UPDATE", "Textedit Update", "Calls the update function every time the property is edited (Only string properties; not operator popups)")]
        return items

    prop_options: bpy.props.EnumProperty(name="Options",
                                    description="Options for this property",
                                    options={"ENUM_FLAG"},
                                    items=get_prop_option_items,
                                    update=_compile)


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
    
    
    category: bpy.props.StringProperty(name="Category", default="OTHER",
                                description="The category this property is displayed in")
    
    def match_settings(self, new_prop):
        new_prop["name"] = self.get_unique_name(self.get("name"))
        new_prop["property_type"] = self.get("property_type")
        new_prop["description"] = self.get("description")
        new_prop["allow_pointers"] = self.get("allow_pointers")
        new_prop["prop_options"] = self.get("prop_options")
        new_prop["category"] = self.get("category")
        for attr in self.settings.copy_attributes:
            new_prop.settings[attr] = self.settings.get(attr)
        self.settings.copy(new_prop.settings)
    
    def copy(self):
        new_prop = self.prop_collection.add()
        self.match_settings(new_prop)
        return new_prop