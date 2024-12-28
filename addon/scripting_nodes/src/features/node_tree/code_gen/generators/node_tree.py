from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import sn_nodes
from scripting_nodes.src.lib.utils.code.format import normalize_indents


def code_gen_node_tree(ntree):
    code = ""
    for node in sn_nodes(ntree):
        if "ROOT_NODE" in node.sn_options:
            code += normalize_indents(node.code) + "\n"
    return code
