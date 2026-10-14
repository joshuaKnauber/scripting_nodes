"""bl_idnames of reference targets, shared by the `Reference(...)` fields
(core/references.py). Adding a variable node means adding it here.
"""

GLOBAL_VARIABLE_NODES = ("SNA_Node_GlobalVariable",)
VARIABLE_NODES = GLOBAL_VARIABLE_NODES + ("SNA_Node_LocalVariable",)

OPERATOR_NODES = ("SNA_Node_Operator",)
MENU_NODES = ("SNA_Node_Menu", "SNA_Node_PieMenu")
# what Open Menu / Shortcut can open
OPENABLE_NODES = MENU_NODES + ("SNA_Node_Panel",)


def open_call(target):
    """(operator idname, {property: expression}) opening a Menu, Pie Menu or
    Panel node's class at the mouse."""
    operator = {
        "SNA_Node_Menu": "wm.call_menu",
        "SNA_Node_PieMenu": "wm.call_menu_pie",
        "SNA_Node_Panel": "wm.call_panel",
    }[target.bl_idname]
    return operator, {"name": repr(target.sn_name("class"))}


def usable_variable(owner, target):
    """Local variables only exist in their own tree."""
    return (
        target.bl_idname != "SNA_Node_LocalVariable" or target.id_data == owner.id_data
    )
