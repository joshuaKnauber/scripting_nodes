def property_type_items(self, context):
    return [
        ("BOOLEAN", "Boolean", "Boolean", "FORCE_CHARGE", 0),
        ("STRING", "String", "String", "SYNTAX_OFF", 1),
        ("INT", "Integer", "Integer", "DRIVER_TRANSFORM", 2),
        ("FLOAT", "Float", "Float", "SEQUENCE_COLOR_01", 3),
        ("ENUM", "Enum", "Enum", "SEQUENCE_COLOR_01", 4),
        ("COLLECTION", "Collection", "Collection", "SEQUENCE_COLOR_01", 5),
    ]
