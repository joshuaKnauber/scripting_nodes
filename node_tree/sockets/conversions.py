CONVERT_UTILS = """

def string_to_int(value):
    if value.isdigit():
        return int(value)
    return 0

def string_to_icon(value):
    if value in bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.keys():
        return bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items[value].value
    return string_to_int(value)

"""



def string_to_bool(python_value):
    return f"bool({python_value})"

def string_to_icon(python_value):
    return f"string_to_icon({python_value})"


def bool_to_string(python_value):
    return f"str({python_value})"

def bool_to_icon(python_value):
    return f"int({python_value})"


def icon_to_string(python_value):
    return f"str({python_value})"

def icon_to_bool(python_value):
    return f"bool({python_value})"



CONVERSIONS = {
    "String": {
        "Boolean": string_to_bool,
        "Icon": string_to_icon,
        "Enum": lambda python_value: python_value,
    },
    "Boolean": {
        "String": bool_to_string,
        "Icon": bool_to_icon,
    },
    "Icon": {
        "String": icon_to_string,
        "Boolean": icon_to_bool,
    },
    "Enum": {
        "String": lambda python_value: python_value,
    }
}