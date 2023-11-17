import bpy


def property_type_items(self, context):
    return [
        ("BOOLEAN", "Boolean", "Boolean", "FORCE_CHARGE", 0),
        ("STRING", "String", "String", "SYNTAX_OFF", 1),
        ("INT", "Integer", "Integer", "DRIVER_TRANSFORM", 2),
        ("FLOAT", "Float", "Float", "SEQUENCE_COLOR_01", 3),
        ("ENUM", "Enum", "Enum", "SEQUENCE_COLOR_01", 4),
        ("COLLECTION", "Collection", "Collection", "SEQUENCE_COLOR_01", 5),
    ]


def property_node_items(self, context):
    return [
        ("SNA_BoolPropertyNode", "Boolean", "Boolean", "FORCE_CHARGE", 0),
        ("STRING", "String", "String", "SYNTAX_OFF", 1),
        ("INT", "Integer", "Integer", "DRIVER_TRANSFORM", 2),
        ("FLOAT", "Float", "Float", "SEQUENCE_COLOR_01", 3),
        ("ENUM", "Enum", "Enum", "SEQUENCE_COLOR_01", 4),
        ("COLLECTION", "Collection", "Collection", "SEQUENCE_COLOR_01", 5),
    ]


def id_type_names():
    id_types = bpy.types.ID.__subclasses__()
    return list(map(lambda x: x.__name__, id_types))


def id_type_items(self, context):
    id_types = bpy.types.ID.__subclasses__()
    return tuple(map(lambda x: (x.__name__, x.__name__, x.__name__), id_types))
