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



def find_path_in_json(path, json):
    keys = path.replace("[", ".").replace("]", "").split('.')[1:]
    item = json
    for key in keys:
        item = item[key]
    return item



def get_item_type(item_type, is_array):
    prop_types = {
        "COLLECTION": "Collection",
        "POINTER": "Pointer",
        str(type(None)): "Pointer",
        "INT": "Integer",
        "FLOAT": "Float",
        "STRING": "String",
        "ENUM": "Enum",
        "BOOLEAN": "Boolean",
    }
    if item_type in prop_types:
        item_type = prop_types[item_type]
    if is_array:
        item_type += " Vector"
    return item_type