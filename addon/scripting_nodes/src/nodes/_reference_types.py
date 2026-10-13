"""bl_idnames of reference targets, shared by the `Reference(...)` fields
(core/references.py). Adding a variable node means adding it here.
"""

GLOBAL_VARIABLE_NODES = ("SNA_Node_GlobalVariable",)
VARIABLE_NODES = GLOBAL_VARIABLE_NODES + ("SNA_Node_LocalVariable",)

OPERATOR_NODES = ("SNA_Node_Operator",)


def usable_variable(owner, target):
    """Local variables only exist in their own tree."""
    return (
        target.bl_idname != "SNA_Node_LocalVariable" or target.id_data == owner.id_data
    )
