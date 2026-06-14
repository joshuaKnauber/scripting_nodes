"""Shared tuples used as `sn_reference_properties` / `sn_class_body_signature`
values. Centralizing them means adding a new property/variable node only
requires editing one place to widen every consumer that accepts "any
property" or "any variable".
"""


VARIABLE_NODES = (
    "SNA_Node_GlobalVariable",
    "SNA_Node_LocalVariable",
)


BOOL_PROPERTY_NODES = ("SNA_Node_BoolProperty",)
INT_PROPERTY_NODES = ("SNA_Node_IntProperty",)
FLOAT_PROPERTY_NODES = ("SNA_Node_FloatProperty",)
NUMBER_PROPERTY_NODES = INT_PROPERTY_NODES + FLOAT_PROPERTY_NODES
STRING_PROPERTY_NODES = ("SNA_Node_StringProperty",)
FLOAT_VECTOR_PROPERTY_NODES = ("SNA_Node_FloatVectorProperty",)
ENUM_PROPERTY_NODES = ("SNA_Node_EnumProperty",)
POINTER_PROPERTY_NODES = ("SNA_Node_PointerProperty",)
COLLECTION_PROPERTY_NODES = ("SNA_Node_CollectionProperty",)


# Every property-flavor node. Used by Get/Set Property and by class-body
# containers (Operator / Preferences / PropertyGroup), which all need a
# broad picker and filter further at apply time.
PROPERTY_NODES = (
    BOOL_PROPERTY_NODES
    + INT_PROPERTY_NODES
    + FLOAT_PROPERTY_NODES
    + STRING_PROPERTY_NODES
    + FLOAT_VECTOR_PROPERTY_NODES
    + ENUM_PROPERTY_NODES
    + POINTER_PROPERTY_NODES
    + COLLECTION_PROPERTY_NODES
)


PROPERTY_GROUP_NODES = ("SNA_Node_PropertyGroup",)


# Composite signature used by the addon's data panel (Properties list shows
# property nodes alongside property groups). Not bound to any consumer
# node - registered explicitly so its backing collection stays alive.
DATA_PANEL_PROPERTY_NODES = PROPERTY_NODES + PROPERTY_GROUP_NODES
