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
            return "[" + (", ").join(list(value)) + "]"
        return "[]"
    return value
    
"""



CONVERSIONS = { # convert KEY to OPTIONS
    "String": {
        "Data": lambda from_out, to_inp: from_out.python_value,
        "Boolean": lambda from_out, to_inp: f"bool({from_out.python_value})",
        "Icon": lambda from_out, to_inp: f"string_to_icon({from_out.python_value})",
        "Enum": lambda from_out, to_inp: from_out.python_value if to_inp.subtype == "NONE" else f"set([{from_out.python_value}])",
    },
    "Boolean": {
        "Data": lambda from_out, to_inp: from_out.python_value,
        "String": lambda from_out, to_inp: f"str({from_out.python_value})",
        "Icon": lambda from_out, to_inp: f"int({from_out.python_value})",
    },
    "Boolean Vector": {
        "Data": lambda from_out, to_inp: from_out.python_value,
        "String": lambda from_out, to_inp: f"str(tuple({from_out.python_value}))",
    },
    "Icon": {
        "Data": lambda from_out, to_inp: from_out.python_value,
        "Integer": lambda from_out, to_inp: from_out.python_value,
        "String": lambda from_out, to_inp: f"icon_to_string({from_out.python_value})",
        "Boolean": lambda from_out, to_inp: f"bool({from_out.python_value})",
    },
    "Enum": {
        "Data": lambda from_out, to_inp: from_out.python_value,
        "String": lambda from_out, to_inp: from_out.python_value if from_out.subtype == "NONE" else f"str({from_out.python_value})",
        "List": lambda from_out, to_inp: f"[{from_out.python_value}]" if from_out.subtype == "NONE" else f"list({from_out.python_value})",

        "ENUM_FLAG": {
            "NONE": lambda from_out, to_inp: f"{from_out.python_value}[0]",
        },
        "NONE": {
            "ENUM_FLAG": lambda from_out, to_inp: f"set([{from_out.python_value}])",
        }
    },
    "Integer": {
        "Data": lambda from_out, to_inp: from_out.python_value,
        "Icon": lambda from_out, to_inp: from_out.python_value,
        "Float": lambda from_out, to_inp: from_out.python_value,
        "String": lambda from_out, to_inp: f"str({from_out.python_value})",
        "Boolean": lambda from_out, to_inp: f"bool({from_out.python_value})",
    },
    "Integer Vector": {
        "Data": lambda from_out, to_inp: from_out.python_value,
        "String": lambda from_out, to_inp: f"str(tuple({from_out.python_value}))",
    },
    "Float": {
        "Data": lambda from_out, to_inp: from_out.python_value,
        "Integer": lambda from_out, to_inp: from_out.python_value,
        "String": lambda from_out, to_inp: f"str({from_out.python_value})",
        "Boolean": lambda from_out, to_inp: f"bool({from_out.python_value})",
    },
    "Float Vector": {
        "Data": lambda from_out, to_inp: from_out.python_value,
        "String": lambda from_out, to_inp: f"str(tuple({from_out.python_value}))",
    },
    "List": {
        "Data": lambda from_out, to_inp: from_out.python_value,
        "Enum": lambda from_out, to_inp: f"set({from_out.python_value})",
        "Float Vector": lambda from_out, to_inp: f"list({from_out.python_value})",
        "Integer Vector": lambda from_out, to_inp: f"list({from_out.python_value})",
        "Boolean Vector": lambda from_out, to_inp: f"list({from_out.python_value})",
    },
    "Property": {
        "Data": lambda from_out, to_inp: from_out.python_value,
        "Collection Property": lambda from_out, to_inp: from_out.python_value,
        "String": lambda from_out, to_inp: f"str({from_out.python_value})",
    },
    "Collection Property": {
        "Data": lambda from_out, to_inp: from_out.python_value,
        "Property": lambda from_out, to_inp: from_out.python_value,
        "String": lambda from_out, to_inp: f"str({from_out.python_value}.keys())",
        "List": lambda from_out, to_inp: f"{from_out.python_value}.values()",
    },
}