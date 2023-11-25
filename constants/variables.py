from . import sockets


def variable_type_items(self, context):
    return [
        ("DATA", "Data", "Data", "MOD_DATA_TRANSFER", 0),
        ("BOOLEAN", "Boolean", "Boolean", "FORCE_CHARGE", 1),
        ("STRING", "String", "String", "SYNTAX_OFF", 2),
        ("INT", "Integer", "Integer", "DRIVER_TRANSFORM", 3),
        ("FLOAT", "Float", "Float", "CON_TRANSLIKE", 4),
        ("LIST", "List", "List", "MOD_ARRAY", 5),
        ("DICT", "Dictionary", "Dictionary", "LINENUMBERS_ON", 6),
        ("POINTER", "Pointer", "Pointer", "MONKEY", 7),
        ("COLLECTION", "Collection", "Collection", "SCENE_DATA", 8),
    ]
