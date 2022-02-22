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



def get_data_items(data, path):
    new_items = {}
    # get attributes
    for attr in dir(data):
        if is_valid_attribute(attr):
            value = getattr(data, attr)
            item_type = get_item_type(str(type(value)), False)
            name = attr
            if hasattr(value, "bl_rna"):
                name = value.bl_rna.name
            if hasattr(data, "bl_rna") and attr in data.bl_rna.properties:
                prop = data.bl_rna.properties[attr]
                name = prop.name
                item_type = get_item_type(prop.type, getattr(prop, "is_array", False))
            name = name.replace("_", " ").title()
            new_items[attr] = get_new_item(name, f"{path}.{attr}", hasattr(value, "bl_rna"), item_type)
    # get items
    if getattr(data, "__iter__", False) and hasattr(data, "keys") and hasattr(data, "values"):
        data_amount = len(data)
        key_amount = len(data.keys())
        for i in range(data_amount):
            indexed = data[i]
            key = None
            if key_amount == data_amount:
                key = data.keys()[i]
                
            item_type = get_item_type("Pointer", False)
            name = f"'{indexed.name}'" if hasattr(indexed, "name") else f"'{key}'" if key else str(i)
            new_items[name] = get_new_item(name, f"{path}['{key}']" if key else f"{path}[{i}]", True, item_type)

            if i >= 20 and data_amount > 25:
                new_items[name]["DETAILS"]["shortened_coll"] = True
                break
    # sort items
    sorted_keys = sorted(new_items.keys(), key=lambda s: new_items[s]["DETAILS"]["type"])
    sorted_keys = sorted(sorted_keys, key=lambda s: new_items[s]["DETAILS"]["has_properties"], reverse=True)
    sorted_items = {}
    for key in sorted_keys: sorted_items[key] = new_items[key]
    return sorted_items
    
    

def get_new_item(name, path, has_properties, item_type):
    new_item = {
        "DETAILS": {
            "expanded": False,
            "type": item_type,
            "name": name,
            "description": "",
            "path": path,
            "has_properties": has_properties,
            "shortened_coll": False,
            "data_search": "",
            "data_filter": filter_defaults,
        }}
    return new_item