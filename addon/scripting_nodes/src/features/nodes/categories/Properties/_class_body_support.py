"""Shared bits for property nodes that can target a class body.

The `register_on` enum on each property node now includes Operator,
Preferences, and PropertyGroup. When one of those is selected the node
emits no code_register/unregister; instead it exposes a
`class_body_annotation()` method that the consuming container node uses
to inject the property into its emitted class.
"""


# Append these to each property node's `register_on` enum items list. Keeping
# the entries here keeps the enum definitions in property nodes mostly
# unchanged while ensuring all class-body targets stay in sync.
CLASS_BODY_REGISTER_ON_ITEMS = [
    ("Operator", "Operator", "Attach to an Operator node's class body", "DOT", 15),
    (
        "Preferences",
        "Preferences",
        "Attach to the addon's preferences class body",
        "PREFERENCES",
        16,
    ),
    (
        "PropertyGroup",
        "Property Group",
        "Attach to a Property Group node's class body",
        "OUTLINER_DATA_POINTCLOUD",
        17,
    ),
]


CLASS_BODY_TARGETS = {"Operator", "Preferences", "PropertyGroup"}


def is_class_body_target(register_on):
    return register_on in CLASS_BODY_TARGETS
