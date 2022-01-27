CONVERT_UTILS = """

def string_to_int(value):
    if value.isdigit():
        return int(value)
    return 0

def string_to_icon(value):
    if value in bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.keys():
        return bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items[value].value
    return string_to_int(value)
    
def icon_to_string(value):
    if value < len(bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items):
        return bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items[value].name
    return ""
    
def enum_set_to_string(value):
    if type(value) == set:
        if len(value) > 0:
            return list(value)[0]
        return "NONE"
    return value
    
"""



CONVERSIONS = { # convert KEY to OPTIONS
    "String": {
        "Data": lambda socket: socket.python_value,
        "Boolean": lambda socket: f"bool({socket.python_value})",
        "Icon": lambda socket: f"string_to_icon({socket.python_value})",
        "Enum": lambda socket: socket.python_value,
    },
    "Boolean": {
        "Data": lambda socket: socket.python_value,
        "String": lambda socket: f"str({socket.python_value})",
        "Icon": lambda socket: f"int({socket.python_value})",
    },
    "Boolean Vector": {
        "Data": lambda socket: socket.python_value,
        "String": lambda socket: f"str(tuple({socket.python_value}))",
    },
    "Icon": {
        "Data": lambda socket: socket.python_value,
        "Integer": lambda socket: socket.python_value,
        "String": lambda socket: f"icon_to_string({socket.python_value})",
        "Boolean": lambda socket: f"bool({socket.python_value})",
    },
    "Enum": {
        "Data": lambda socket: socket.python_value,
        "String": lambda socket: f"enum_set_to_string({socket.python_value})",

        "ENUM_FLAG": {
            "NONE": lambda socket: f"enum_set_to_string({socket.python_value})",
        },
        "NONE": {
            "ENUM_FLAG": lambda socket: f"set([{socket.python_value}])",
        }
    },
    "Integer": {
        "Data": lambda socket: socket.python_value,
        "Icon": lambda socket: socket.python_value,
        "Float": lambda socket: socket.python_value,
        "String": lambda socket: f"str({socket.python_value})",
        "Boolean": lambda socket: f"bool({socket.python_value})",
    },
    "Integer Vector": {
        "Data": lambda socket: socket.python_value,
        "String": lambda socket: f"str(tuple({socket.python_value}))",
    },
    "Float": {
        "Data": lambda socket: socket.python_value,
        "Integer": lambda socket: socket.python_value,
        "String": lambda socket: f"str({socket.python_value})",
        "Boolean": lambda socket: f"bool({socket.python_value})",
    },
    "Float Vector": {
        "Data": lambda socket: socket.python_value,
        "String": lambda socket: f"str(tuple({socket.python_value}))",
    },
    "List": {
        "Data": lambda socket: socket.python_value,
        "Float Vector": lambda socket: f"list({socket.python_value})",
        "Integer Vector": lambda socket: f"list({socket.python_value})",
        "Boolean Vector": lambda socket: f"list({socket.python_value})",
    },
    "Property": {
        "Data": lambda socket: socket.python_value_pointer,
        "Collection Property": lambda socket: socket.python_value,
        "String": lambda socket: f"str({socket.python_value_pointer})",
    },
    "Collection Property": {
        "Data": lambda socket: socket.python_value_pointer,
        "Property": lambda socket: socket.python_value,
        "String": lambda socket: f"str({socket.python_value_pointer}.keys())",
        "List": lambda socket: f"{socket.python_value_pointer}.values()", # TODO only collections
    },
    "Data": {
        "String": lambda socket: socket.python_value,
        "Boolean": lambda socket: socket.python_value,
        "Icon": lambda socket: socket.python_value,
        "Enum": lambda socket: socket.python_value,
        "Integer": lambda socket: socket.python_value,
        "Float": lambda socket: socket.python_value,
        "List": lambda socket: socket.python_value,
        "Blend Data": lambda socket: socket.python_value,
    },
}