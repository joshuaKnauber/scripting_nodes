import bpy
from ..addon.properties.settings.settings import property_icons



def is_valid_attribute(attr):
    return not attr in ["rna_type", "original", "bl_rna"] and not attr[0] == "_"

filter_items = [("Pointer", "Pointer", "Pointer", property_icons["Property"], 1),
    ("Collection", "Collection", "Collection", property_icons["Collection"], 2),
    ("List", "List", "List", property_icons["List"], 4),
    ("String", "String", "String", property_icons["String"], 8),
    ("Enum", "Enum", "Enum", property_icons["Enum"], 16),
    ("Boolean", "Boolean", "Boolean", property_icons["Boolean"], 32),
    ("Boolean Vector", "Boolean Vector", "Boolean Vector", property_icons["Boolean"], 64),
    ("Integer", "Integer", "Integer", property_icons["Integer"], 128),
    ("Integer Vector", "Integer Vector", "Integer Vector", property_icons["Integer"], 256),
    ("Float", "Float", "Float", property_icons["Float"], 512),
    ("Float Vector", "Float Vector", "Float Vector", property_icons["Float"], 1024),
    ("Function", "Function", "Function", property_icons["Function"], 2048),
    ("Built In Function", "Built In Function", "Built In Function", property_icons["Built In Function"], 4096)]

filter_defaults = {"Pointer","Collection","List","String","Enum","Boolean","Boolean Vector",
    "Integer","Integer Vector","Float","Float Vector","Function"}
    


class SN_DataProperty(bpy.types.PropertyGroup):
    
    def create_items(self):
        if not self.items_added:
            bpy.context.scene.sn.create_data_items(eval(self.path), self.path)
            
    def delete_items(self):
        sn = bpy.context.scene.sn
        for i in range(len(sn.data_items)-1, -1, -1):
            if self.path in sn.data_items[i].parent_path:
                sn.data_items.remove(i)
        self.items_added = False
    
    def update_expand(self, context):
        if not self.items_added and self.has_properties:
            self.create_items()
            self.items_added = True
            
    def reload_items(self):
        self.delete_items()
        self.create_items()


    name: bpy.props.StringProperty()

    identifier: bpy.props.StringProperty()

    description: bpy.props.StringProperty()

    type: bpy.props.StringProperty()

    path: bpy.props.StringProperty()

    parent_path: bpy.props.StringProperty()
    
        
    has_properties: bpy.props.BoolProperty()
    
    items_added: bpy.props.BoolProperty(default=False)
    
    expand: bpy.props.BoolProperty(default=False,
                                update=update_expand,
                                name="Expand",
                                description="Expand the items of this property")
    
    data_filter: bpy.props.EnumProperty(name="Type",
                                        options={"ENUM_FLAG"},
                                        description="Filter by data type",
                                        items=filter_items,
                                        default=filter_defaults)

    data_search: bpy.props.StringProperty(name="Search",
                                        description="Search data",
                                        options={"TEXTEDIT_UPDATE"})