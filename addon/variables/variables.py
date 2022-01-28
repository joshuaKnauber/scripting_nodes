import bpy
from ...utils import unique_collection_name



class SN_VariableProperties(bpy.types.PropertyGroup):
    
    def compile(self, context=None):
        pass
    
    
    @property
    def data_path(self):
        return ""
    
    
    @property
    def icon(self):
        return "MONKEY"
    
    
    def get_name(self):
        return self.get("name", "Variable Default")

    def set_name(self, value):
        names = list(map(lambda item: item.name, list(filter(lambda item: item!=self, self.prop_collection))))
        value = unique_collection_name(value, "New Variable", names, " ")

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