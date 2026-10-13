"""Reference fields: a variable used in its tree and from another tree, a
deleted target, a button picking an operator, the sidebar showing
the users of the selected variable."""

import helpers


SIDEBAR_TAB = "Node"


def setup():
    other = helpers.new_tree("Settings")
    tree = helpers.new_tree("Demo")
    var = helpers.add_node(tree, "SNA_Node_GlobalVariable", (-500, 200))
    var.name = "Counter"
    get = helpers.add_node(tree, "SNA_Node_GetVariable", (-150, 250))
    helpers.point(get, "var", var)
    gone = helpers.add_node(tree, "SNA_Node_GlobalVariable", (-500, -100))
    set_var = helpers.add_node(tree, "SNA_Node_SetVariable", (-150, 50))
    helpers.point(set_var, "var", gone)
    tree.nodes.remove(gone)
    remote = helpers.add_node(other, "SNA_Node_GetVariable")
    helpers.point(remote, "var", var)

    op = helpers.add_node(tree, "SNA_Node_Operator", (200, 250))
    button = helpers.add_node(tree, "SNA_Node_Button", (200, -50))
    helpers.point(button, "operator_sn", op)

    for node in tree.nodes:
        node.select = False
    var.select = True
    tree.nodes.active = var
    helpers.flush()
    return tree
