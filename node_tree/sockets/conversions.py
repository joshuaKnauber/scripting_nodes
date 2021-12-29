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
    
"""



CONVERSIONS = { # convert KEY to OPTIONS
    "String": {
        "Data": lambda python_value: python_value,
        "Boolean": lambda python_value: f"bool({python_value})",
        "Icon": lambda python_value: f"string_to_icon({python_value})",
        "Enum": lambda python_value: python_value,
    },
    "Boolean": {
        "Data": lambda python_value: python_value,
        "String": lambda python_value: f"str({python_value})",
        "Icon": lambda python_value: f"int({python_value})",
    },
    "Boolean Vector": {
        "Data": lambda python_value: python_value,
        "String": lambda python_value: f"str(tuple({python_value}))",
    },
    "Icon": {
        "Data": lambda python_value: python_value,
        "String": lambda python_value: f"icon_to_string({python_value})",
        "Boolean": lambda python_value: f"bool({python_value})",
    },
    "Enum": {
        "Data": lambda python_value: python_value,
        "String": lambda python_value: python_value,
    },
    "Integer": {
        "Data": lambda python_value: python_value,
        "Float": lambda python_value: python_value,
        "Factor": lambda python_value: python_value,
    },
    "Integer Vector": {
        "Data": lambda python_value: python_value,
        "String": lambda python_value: f"str(tuple({python_value}))",
    },
    "Float": {
        "Data": lambda python_value: python_value,
        "Integer": lambda python_value: python_value,
        "Factor": lambda python_value: python_value,
    },
    "Float Vector": {
        "Data": lambda python_value: python_value,
        "String": lambda python_value: f"str(tuple({python_value}))",
    },
    "Factor": {
        "Data": lambda python_value: python_value,
        "Integer": lambda python_value: python_value,
        "Float": lambda python_value: python_value,
    },
    "Data": {
        "String": lambda python_value: python_value,
        "Boolean": lambda python_value: python_value,
        "Icon": lambda python_value: python_value,
        "Enum": lambda python_value: python_value,
        "Float": lambda python_value: python_value,
        "Factor": lambda python_value: python_value,
    },
}