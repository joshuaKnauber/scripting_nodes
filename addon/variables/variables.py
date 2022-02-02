import bpy
from ...utils import get_python_name, unique_collection_name
from ..properties.settings.settings import property_icons



class SN_VariableProperties(bpy.types.PropertyGroup):
    
    def compile(self, context=None):
        pass
    
    
    @property
    def node_tree(self):
        return self.id_data
    
    
    @property
    def python_name(self):
        names = []
        for var in self.node_tree.variables:
            if var == self:
                break
            names.append(var.python_name)
        
        name = unique_collection_name(f"sna_{get_python_name(self.name, 'new_variable')}", "new_variable", names, "_")
        return name


    @property
    def data_path(self):
        return f"SN_VAR_{self.python_name}"
    
    
    @property
    def icon(self):
        return "MONKEY"
    
    
    def compile(self, context=None):
        """ Registers the variable and unregisters previous version """
        # unregister previous
        if self.python_name in self.node_tree.variable_cache:
            del self.node_tree.variable_cache[self.python_name]
        # register
        self.node_tree.variable_cache[self.python_name] = ""
        print(f"Serpens Log: Variable {self.name} received an update")
    
    
    def get_name(self):
        return self.get("name", "Variable Default")

    def set_name(self, value):
        names = list(map(lambda item: item.name, list(filter(lambda item: item!=self, self.node_tree.variables))))
        value = unique_collection_name(value, "New Variable", names, " ")

        self["name"] = value
        return # TODO

        # get nodes to update references
        to_update_nodes = []
        key = "prop_group" if self.property_type == "Group" else "prop_name"
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                for node in ntree.nodes:
                    if hasattr(node, key) and getattr(node, key) == self.name:
                        to_update_nodes.append((node, key))

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
    
    name: bpy.props.StringProperty(name="Variable Name",
                                    description="Name of this variable",
                                    default="Variable Default",
                                    get=get_name,
                                    set=set_name,
                                    update=compile)
    
    
    variable_type: bpy.props.EnumProperty(name="Type",
                                    description="The type of data this variable stores",
                                    update=compile,
                                    items=[("Data", "Data", "Stores any type of data", property_icons["Data"], 0),
                                           ("Boolean", "Boolean", "Stores True or False", property_icons["Boolean"], 1),
                                           ("Float", "Float", "Stores a decimal number", property_icons["Float"], 2),
                                           ("Integer", "Integer", "Stores an integer number", property_icons["Integer"], 3),
                                           ("Pointer", "Pointer", "Stores a reference to certain types of blend data, collection or group properties", property_icons["Pointer"], 4),
                                           ("Collection", "Collection", "Stores a list of certain blend data or property groups to be displayed in lists", property_icons["Collection"], 5)])