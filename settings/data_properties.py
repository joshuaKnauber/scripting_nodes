import bpy
from ..addon.properties.settings.settings import property_icons



def is_valid_attribute(attr):
    return not attr in ["rna_type", "original", "bl_rna"] and not attr[0] == "_"


filter_items = [("Pointer", "Pointer", "Pointer", property_icons["Property"], 1),
    ("Collection", "Collection", "Collection", property_icons["Collection"], 2),
    ("List", "List", "List", property_icons["List"], 4),
    ("String", "String", "String", property_icons["String"], 8),
    ("Boolean", "Boolean", "Boolean", property_icons["Boolean"], 32),
    ("Boolean Vector", "Boolean Vector", "Boolean Vector", property_icons["Boolean"], 64),
    ("Integer", "Integer", "Integer", property_icons["Integer"], 128),
    ("Integer Vector", "Integer Vector", "Integer Vector", property_icons["Integer"], 256),
    ("Float", "Float", "Float", property_icons["Float"], 512),
    ("Float Vector", "Float Vector", "Float Vector", property_icons["Float"], 1024),
    ("Function", "Function", "Function", property_icons["Function"], 2048) ]


filter_defaults = {"Pointer","Collection","List","String","Boolean","Boolean Vector",
    "Integer","Integer Vector","Float","Float Vector","Function"}


def is_iterable(data):
    if hasattr(data, "keys") and hasattr(data, "values"):
        return hasattr(data, "__getitem__")
    return False


def get_data_items(path, data):
    data_items = {}

    # get attributes
    data_dict = data if type(data) == dict else data_to_dict(data)
    for key in data_dict.keys():
        data_items[key] = get_data_item(data_dict[key], path, key)

    # get items for iterable
    if is_iterable(data) and not type(data) == dict:
        # get keyed items
        if len(data.keys()) == len(data.values()):
            for key in data.keys():
                if hasattr(data[key], "bl_rna"):
                    data_items[f"'{key}'"] = get_data_item(data[key], path, f"'{key}'")
        # get indexed items
        else:
            for i in range(len(data.values())):
                data_items[f"{i}"] = get_data_item(data[i], path, f"{i}")

    # sort items
    sorted_keys = sorted(data_items.keys(), key=lambda s: data_items[s]["type"])
    sorted_keys = sorted(sorted_keys, key=lambda s: data_items[s]["has_properties"], reverse=True)
    sorted_items = {}
    for key in sorted_keys: sorted_items[key] = data_items[key]
    return sorted_items


def data_to_dict(data):
    """ Converts the given data to a dictionary with keys for the path section and the data """
    data_dict = {}
    for attribute in dir(data):
        if is_valid_attribute(attribute):
            data_dict[attribute] = getattr(data, attribute)
    return data_dict
        
        
def get_data_item(data, path, attribute):
    """ Returns a data object for the given data its path and the datas attribute """
    has_properties = hasattr(data, "bl_rna")
    if (attribute[0] == "'" and attribute[-1] == "'") or attribute.isdigit():
        new_path = f"{path}[{attribute}]"
        has_properties = True
    else:
        new_path = f"{path}.{attribute}"

    data_item = {
        "name": get_data_name(data, attribute),
        "path": new_path,
        "type": get_item_type(data),
        "data": data,
        "data_search": "",
        "data_filter": filter_defaults,
        "expanded": False,
        "has_properties": has_properties,
        "properties": {}
    }
    return data_item


def get_data_name(data, attribute):
    """ Returns a name based on the given attribute name """
    if (attribute[0] == "'" and attribute[-1] == "'") or attribute.isdigit():
        return f"[{attribute}]"
    name = attribute.replace("_", " ").title()
    if hasattr(data, "bl_rna"):
        name = f"{name} ({data.bl_rna.name})"
    return name


def get_item_type(data):
    """ Returns the item type for the given data """
    item_type = str(type(data))
    if "bpy_prop_collection" in item_type: item_type = "Collection"
    elif "bpy_types" in item_type: item_type = "Pointer"
    elif "bpy.types" in item_type: item_type = "Pointer"
    elif hasattr(type(data), "bl_rna"): item_type = "Pointer"
    elif "None" in item_type: item_type = "Pointer"
    elif "bpy_func" in item_type: item_type = "Function"
    elif "str" in item_type: item_type = "String"
    elif "bool" in item_type: item_type = "Boolean"
    elif "float" in item_type: item_type = "Float"
    elif "int" in item_type: item_type = "Integer"
    elif "Color" in item_type: item_type = "Float Vector"
    elif "Euler" in item_type: item_type = "Float Vector"
    elif "Quaternion" in item_type: item_type = "Float Vector"
    elif "Matrix" in item_type: item_type = "List"
    elif "list" in item_type: item_type = "List"
    elif ("tuple" in item_type or "Vector" in item_type or "bpy_prop_array" in item_type) and len(data):
        if "float" in str(type(data[0])): item_type = "Float Vector"
        elif "int" in str(type(data[0])): item_type = "Integer Vector"
        elif "bool" in str(type(data[0])): item_type = "Boolean Vector"
        else: item_type = "List"
    return item_type


def separate_attribute_from_path(path):
    """ Returns the last attribute from the path and the path before """
    attr_path = ".".join(path.split(".")[:-1])
    attribute = path.split(".")[-1]
    if path[-1] == "]":
        attribute = path.split("['")[-1][:-2]
        attr_path = "['".join(path.split("['")[:-1])
    return attr_path, f"'{attribute}'"


def item_from_path(data, path):
    """ Returns the item in the data for the given path. Works for anything above bpy.xyz """
    # after bpy.xyz
    if len(path.split(".")) > 2:
        path_sections = bpy_to_path_sections(path)
        curr_item = data[path_sections[0]][path_sections[1]]
        for key in path_sections[2:]:
            curr_item = curr_item["properties"][key]
        return curr_item
    # bpy
    elif len(path.split(".")) == 1:
        return bpy
    # bpy.xyz
    else:
        return data[path.split(".")[-1]]


def bpy_to_path_sections(path):
    """ Takes a blender python data path and converts it to json path sections """
    # TODO this needs to be different e.g for:
    # - bpy.context.window_manager.keyconfigs.addon.keymaps['Node Editor'].keymap_items['sn.force_compile']
    # - bpy.data.objects["Cube"].modifiers["GeometryNodes"]["Output_2_attribute_name"]
    path = path.replace('"', "'").replace("bpy.", "")
    split_path = []
    for section in path.split("['"):
        if not "']" in section:
            split_path += list(filter(lambda s: s, section.split(".")))
        else:
            section = list(filter(lambda s: s, section.split("']")))
            split_path.append(f"'{section[0]}'")
            if len(section) > 1:
                split_path += list(filter(lambda s: s, section[1].split(".")))
    return split_path