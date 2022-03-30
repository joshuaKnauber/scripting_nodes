import bpy
from ...utils import get_python_name, unique_collection_name
from ..properties.settings.settings import property_icons
from ...nodes.compiler import compile_addon



class SN_VariableProperties(bpy.types.PropertyGroup):
    
    
    @property
    def node_tree(self):
        return self.id_data
    
    
    # cache python names so they only have to be generated once
    cached_python_name: bpy.props.StringProperty()
    cached_human_name: bpy.props.StringProperty()
    
    @property
    def python_name(self):
        if self.name == self.cached_human_name and self.cached_python_name: return self.cached_python_name
        
        names = []
        for var in self.node_tree.variables:
            if var == self:
                break
            names.append(var.python_name)
        
        name = unique_collection_name(f"sna_{get_python_name(self.name, 'sna_new_variable')}", "sna_new_variable", names, "_")
        self.cached_python_name = name
        self.cached_human_name = self.name
        return name


    @property
    def data_path(self):
        return f"{self.node_tree.python_name}['{self.python_name}']"
    
    
    @property
    def icon(self):
        return property_icons[self.variable_type]
    
    
    def compile(self, context=None):
        """ Registers the variable and unregisters previous version """
        # print(f"Serpens Log: Variable {self.name} received an update")
        compile_addon()
    
    
    def get_name(self):
        return self.get("name", "Variable Default")
    
    
    def get_to_update_nodes(self):
        to_update_nodes = []
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                for node in ntree.nodes:
                    if getattr(node, "var_name", None) == self.name:
                        to_update_nodes.append(node)
        return to_update_nodes

    def set_name(self, value):
        names = list(map(lambda item: item.name, list(filter(lambda item: item!=self, self.node_tree.variables))))
        value = unique_collection_name(value, "New Variable", names, " ")
        to_update = self.get_to_update_nodes()

        # set value
        self["name"] = value
        self.compile()

        # update node references
        for node in to_update:
            node.var_name = value
    
    name: bpy.props.StringProperty(name="Variable Name",
                                    description="Name of this variable",
                                    default="Variable Default",
                                    get=get_name,
                                    set=set_name,
                                    update=compile)
    
    
    def update_variable_type(self, context):
        for node in self.get_to_update_nodes():
            if hasattr(node, "on_var_changed"):
                node.on_var_changed()
        self.compile()
        
    variable_type: bpy.props.EnumProperty(name="Type",
                                    description="The type of data this variable stores",
                                    update=update_variable_type,
                                    items=[("Data", "Data", "Stores any type of data", property_icons["Data"], 0),
                                           ("String", "String", "Stores a string of characters", property_icons["String"], 1),
                                           ("Boolean", "Boolean", "Stores True or False", property_icons["Boolean"], 2),
                                           ("Float", "Float", "Stores a decimal number", property_icons["Float"], 3),
                                           ("Integer", "Integer", "Stores an integer number", property_icons["Integer"], 4),
                                           ("List", "List", "Stores a list of data", property_icons["List"], 5),
                                           ("Pointer", "Pointer", "Stores a reference to certain types of blend data, collection or group properties", property_icons["Pointer"], 6),
                                           ("Collection", "Collection", "Stores a list of certain blend data or property groups to be displayed in lists", property_icons["Collection"], 7)])
                                           
    string_default: bpy.props.StringProperty(name="Default", description="Default value for the variable", update=compile)
    boolean_default: bpy.props.BoolProperty(name="Default", description="Default value for the variable", update=compile)
    float_default: bpy.props.FloatProperty(name="Default", description="Default value for the variable", update=compile)
    integer_default: bpy.props.IntProperty(name="Default", description="Default value for the variable", update=compile)


    @property
    def var_default(self):
        return {
            "Data": None,
            "String": f"'{self.string_default}'",
            "Boolean": self.boolean_default,
            "Float": self.float_default,
            "Integer": self.integer_default,
            "List": [],
            "Pointer": None,
            "Collection": None,
        }[self.variable_type]