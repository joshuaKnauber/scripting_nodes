import bpy
from ..addon.properties.settings.settings import property_icons


def is_valid_attribute(attr):
    ignore_attributes = ["rna_type", "original",
                         "bl_rna", "evaluated_depsgraph_get"]
    return not attr in ignore_attributes and not attr[0] == "_"


filter_items = [("Pointer", "Pointer", "Pointer", property_icons["Property"], 1),
                ("Collection", "Collection", "Collection",
                 property_icons["Collection"], 2),
                ("List", "List", "List", property_icons["List"], 4),
                ("String", "String/Enum", "Strings and Enums",
                 property_icons["String"], 8),
                ("Enum Set", "Enum Set", "Enum Set",
                 property_icons["Enum Set"], 32),
                ("Boolean", "Boolean", "Boolean",
                 property_icons["Boolean"], 64),
                ("Boolean Vector", "Boolean Vector",
                 "Boolean Vector", property_icons["Boolean"], 128),
                ("Integer", "Integer", "Integer",
                 property_icons["Integer"], 256),
                ("Integer Vector", "Integer Vector",
                 "Integer Vector", property_icons["Integer"], 512),
                ("Float", "Float", "Float", property_icons["Float"], 1024),
                ("Float Vector", "Float Vector",
                 "Float Vector", property_icons["Float"], 2048),
                ("Function", "Function", "Function", property_icons["Function"], 4096)]


filter_defaults = {"Pointer", "Collection", "List", "String", "Enum Set", "Boolean", "Boolean Vector",
                   "Integer", "Integer Vector", "Float", "Float Vector", "Function"}


def is_iterable(data):
    if hasattr(data, "keys") and hasattr(data, "values"):
        return hasattr(data, "__getitem__")
    return False


def add_additional_data(data_dict, path):
    if ".outputs[" in path:
        data_dict["links"] = list(eval(path+".links"))
    return data_dict


def get_data_items(path, data):
    data_items = {}

    # get attributes
    data_dict = validate_data_dict(data) if type(
        data) == dict else data_to_dict(data)
    data_dict = add_additional_data(data_dict, path)
    for key in data_dict.keys():
        item = get_data_item(data, data_dict[key], path, key)
        if item:
            data_items[key] = item

    # get items for iterable
    if is_iterable(data) and not type(data) == dict:
        # get keyed items
        if len(data.keys()) == len(data.values()):
            for key in data.keys():
                if hasattr(data[key], "bl_rna"):
                    item = get_data_item(data, data[key], path, f"'{key}'")
                    if item:
                        data_items[f"'{key}'"] = item
        # get indexed items
        else:
            max_items = 21
            for i in range(min(len(data.values()), max_items)):
                item = get_data_item(data, data[i], path, f"{i}")
                if item:
                    data_items[f"{i}"] = item
                    if i == max_items-1 and len(data.values()) > max_items:
                        data_items[f"{i}"]["clamped"] = True

    # sort items
    sorted_keys = sorted(
        data_items.keys(), key=lambda s: data_items[s]["type"])
    sorted_keys = sorted(
        sorted_keys, key=lambda s: data_items[s]["has_properties"], reverse=True)
    sorted_items = {}
    for key in sorted_keys:
        sorted_items[key] = data_items[key]
    return sorted_items


def validate_data_dict(data):
    """ Removes all attributes that aren't valid """
    to_delete = []
    for key in data.keys():
        if not is_valid_attribute(key):
            to_delete.append(key)
    for key in to_delete:
        del data[key]
    return data


def data_to_dict(data):
    """ Converts the given data to a dictionary with keys for the path section and the data """
    data_dict = {}
    attributes = dir(data)
    if hasattr(data, "keyframe_insert"):
        attributes += dir(bpy.types.Struct)
        attributes.sort()
    for attribute in attributes:
        if is_valid_attribute(attribute):
            data_dict[attribute] = getattr(data, attribute)
    return data_dict


def get_data_item(parent_data, data, path, attribute):
    """ Returns a data object for the given data its path and the datas attribute """
    try:
        data
        has_properties = hasattr(
            data, "bl_rna") or "bpy_prop_collection" in str(type(data))
        if (attribute[0] == "'" and attribute[-1] == "'") or attribute.isdigit():
            new_path = f"{path}[{attribute}]"
            has_properties = True
        else:
            new_path = f"{path}.{attribute}"

        data_item = {
            "name": get_data_name(data, attribute),
            "path": new_path,
            "required": "",
            "type": get_item_type(data),
            "data": data,
            "data_search": "",
            "data_filter": filter_defaults,
            "expanded": False,
            "has_properties": has_properties,
            "properties": {},
            "clamped": False,
        }
        if data_item["type"] == "Function":
            data_item["path"] += get_function_parameters(
                parent_data, attribute)
            data_item["required"] += get_required_function_parameters(
                parent_data, attribute)
        return data_item
    except:
        return None


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
    if "bpy_prop_collection" in item_type:
        item_type = "Collection"
    elif "bpy_types" in item_type:
        item_type = "Pointer"
    elif "bpy.types" in item_type:
        item_type = "Pointer"
    elif hasattr(type(data), "bl_rna"):
        item_type = "Pointer"
    elif "None" in item_type:
        item_type = "Pointer"
    elif "bpy_func" in item_type or "builtin_function_or_method" in item_type:
        item_type = "Function"
    elif "set" in item_type:
        item_type = "Enum Set"
    elif "str" in item_type:
        item_type = "String"
    elif "bool" in item_type:
        item_type = "Boolean"
    elif "float" in item_type:
        item_type = "Float"
    elif "int" in item_type:
        item_type = "Integer"
    elif "Color" in item_type:
        item_type = "Float Vector"
    elif "Euler" in item_type:
        item_type = "Float Vector"
    elif "Quaternion" in item_type:
        item_type = "Float Vector"
    elif "Matrix" in item_type:
        item_type = "List"
    elif "list" in item_type:
        item_type = "List"
    elif ("tuple" in item_type or "Vector" in item_type or "bpy_prop_array" in item_type) and len(data):
        if "float" in str(type(data[0])):
            item_type = "Float Vector"
        elif "int" in str(type(data[0])):
            item_type = "Integer Vector"
        elif "bool" in str(type(data[0])):
            item_type = "Boolean Vector"
        else:
            item_type = "List"
    return item_type


def get_special_function_params(attribute):
    """ Returns the special parameters for the given function """
    if attribute == "keyframe_insert":
        return "data_path: String, index: Integer, frame: Integer, group: String, options: Enum Set['INSERTKEY_NEEDED','INSERTKEY_VISUAL','INSERTKEY_XYZ_TO_RGB','INSERTKEY_REPLACE','INSERTKEY_AVAILABLE','INSERTKEY_CYCLE_AWARE'], "
    elif attribute == "keyframe_delete":
        return "data_path: String, index: Integer, frame: Integer, group: String, "
    elif attribute == "driver_add":
        return "path*: String, index*: Integer, "
    elif attribute == "driver_remove":
        return "path*: String, index*: Integer, "
    return ""


def get_special_function_outputs(attribute):
    """ Returns the special outputs for the given function """
    if attribute == "as_pointer":
        return "adress: Integer, "
    elif attribute == "keyframe_insert":
        return "success: Boolean, "
    elif attribute == "keyframe_delete":
        return "success: Boolean, "
    elif attribute == "driver_add":
        return "fcurve: Data, "
    elif attribute == "driver_remove":
        return "success: Boolean, "
    return ""


def get_special_required_parameters(attribute):
    """ Returns the special required parameters for the given function """
    if attribute == "keyframe_insert":
        return "data_path"
    elif attribute == "keyframe_delete":
        return "data_path"
    elif attribute == "driver_add":
        return "path*"
    elif attribute == "driver_remove":
        return "path*"
    return ""


def get_function_parameters(parent_data, name):
    """ Returns a dictionary with function parameters """
    params = ""
    outputs = ""
    if hasattr(parent_data, "bl_rna") and hasattr(parent_data.bl_rna, "functions"):
        if name in parent_data.bl_rna.functions:
            for param in parent_data.bl_rna.functions[name].parameters:
                param_type = param.type.title()
                if param_type == "Str":
                    param_type = "String"
                elif param_type == "Int":
                    param_type = "Integer"
                if getattr(param, "is_array", False):
                    param_type += " Vector"
                if param_type == "Enum":
                    if param.is_enum_flag:
                        param_type = "Enum Set"
                    items = ",".join(
                        list(map(lambda item: f"'{item.identifier}'", param.enum_items_static)))
                    param_type += f"[{items}]"
                if param.is_output:
                    outputs += f"{param.identifier}: {param_type}, "
                else:
                    params += f"{param.identifier}: {param_type}, "
        else:
            params = get_special_function_params(name)
            outputs = get_special_function_outputs(name)
    if params:
        params = params[:-2]
    if outputs:
        outputs = outputs[:-2]
    params = f"({params})"
    if outputs:
        params += f" = {outputs}"
    return params


def get_required_function_parameters(parent_data, name):
    """ Returns a string separated by ; with the required function parameters """
    required = ""
    if hasattr(parent_data, "bl_rna") and hasattr(parent_data.bl_rna, "functions"):
        if name in parent_data.bl_rna.functions:
            for param in parent_data.bl_rna.functions[name].parameters:
                if param.is_required:
                    required += param.identifier if not required else f";{param.identifier}"
        else:
            required = get_special_required_parameters(name)
    return required


def item_from_path(data, path):
    """ Returns the item in the data for the given path. Works for anything above bpy.xyz """
    # after bpy.xyz
    if len(path.split(".")) > 2:
        path_sections = bpy_to_path_sections(path, False)
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


def bpy_to_path_sections(path, keep_brackets=True):
    """ Takes a blender python data path and converts it to json path sections """
    if len(path) >= 4 and path[:4] == "bpy.":
        path = path[4:]

    sections = []
    curr_section = ""
    bracket_level = 0
    in_string = False
    for char in path:
        if in_string:
            curr_section += char
            if char == "'" or char == '"':
                in_string = False
        else:
            if char == "." and bracket_level == 0:
                sections.append(curr_section)
                curr_section = ""
            elif char == "'" or char == '"':
                in_string = True
                curr_section += char
            elif char == "[":
                if bracket_level == 0:
                    sections.append(curr_section)
                    curr_section = "[" if keep_brackets else ""
                    bracket_level = 1
                else:
                    bracket_level += 1
                    curr_section += "["
            elif char == "]":
                bracket_level -= 1
                if keep_brackets or bracket_level > 0:
                    curr_section += "]"
            else:
                curr_section += char
    sections.append(curr_section)
    sections = list(filter(lambda item: item, sections))
    return sections


def bpy_to_indexed_sections(path):
    """ Takes a blender python data path and converts it to indexed path sections """
    # combine indexed sections
    combined = ["bpy"]
    for section in bpy_to_path_sections(path):
        if (section[0] == "[" and section[-1] == "]") and not combined[-1][-1] == "]":
            combined[-1] += section
        else:
            combined.append(section)

    if not "bpy." in path:
        combined = combined[1:]
    return combined


def join_sections(sections):
    """ Returns the given sections joined to a valid data path """
    data_path = ""
    for i, section in enumerate(sections):
        if i == 0 or section[0] == "[":
            data_path += section
        else:
            data_path += f".{section}"
    return data_path
