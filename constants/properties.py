import bpy


def property_type_items(self, context):
    return [
        ("BOOLEAN", "Boolean", "Boolean", "FORCE_CHARGE", 0),
        ("STRING", "String", "String", "SYNTAX_OFF", 1),
        ("INT", "Integer", "Integer", "DRIVER_TRANSFORM", 2),
        ("FLOAT", "Float", "Float", "CON_TRANSLIKE", 3),
        ("ENUM", "Enum", "Enum", "PRESET", 4),
        ("POINTER", "Pointer", "Pointer", "MONKEY", 5),
        ("COLLECTION", "Collection", "Collection", "SCENE_DATA", 6),
    ]


def property_node_items(self, context):
    return [
        ("SNA_BoolPropertyNode", "Boolean", "Boolean", "FORCE_CHARGE", 0),
        ("STRING", "String", "String", "SYNTAX_OFF", 1),
        ("INT", "Integer", "Integer", "DRIVER_TRANSFORM", 2),
        ("FLOAT", "Float", "Float", "CON_TRANSLIKE", 3),
        ("ENUM", "Enum", "Enum", "PRESET", 4),
        ("POINTER", "Pointer", "Pointer", "MONKEY", 5),
        ("COLLECTION", "Collection", "Collection", "SCENE_DATA", 6),
    ]


NODES = {
    "SNA_NodeBoolProperty": "BOOLEAN",
    # "SNA_NodeBoolProperty": "STRING", # TODO
    # "SNA_NodeBoolProperty": "INT",
    # "SNA_NodeBoolProperty": "FLOAT",
    # "SNA_NodeBoolProperty": "ENUM",
    # "SNA_NodeBoolProperty": "POINTER",
    # "SNA_NodeBoolProperty": "COLLECTION",
}


def id_type_names():
    id_types = bpy.types.ID.__subclasses__()
    return list(map(lambda x: x.__name__, id_types))


def id_type_items(self, context):
    id_types = bpy.types.ID.__subclasses__()
    return tuple(map(lambda x: (x.__name__, x.__name__, x.__name__), id_types))
