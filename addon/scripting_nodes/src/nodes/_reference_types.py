"""bl_idnames of reference targets, shared by the `Reference(...)` fields
(core/references.py). Adding a property/variable node means adding it here.
"""

GLOBAL_VARIABLE_NODES = ("SNA_Node_GlobalVariable",)
VARIABLE_NODES = GLOBAL_VARIABLE_NODES + ("SNA_Node_LocalVariable",)


def usable_variable(owner, target):
    """Local variables only exist in their own tree."""
    return (
        target.bl_idname != "SNA_Node_LocalVariable" or target.id_data == owner.id_data
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


# Every property node (Get/Set Property, attached class properties)
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

OPERATOR_NODES = ("SNA_Node_Operator",)
