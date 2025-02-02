from scripting_nodes.src.lib.libraries import autopep8
from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import sn_nodes
from scripting_nodes.src.lib.utils.code.format import normalize_indents
import bpy


def code_gen_node_tree(ntree):
    code = ""

    # global scope code
    for node in sn_nodes(ntree):
        if node.code_global:
            code += normalize_indents(node.code_global) + "\n"

    # root nodes
    for node in sn_nodes(ntree):
        if "ROOT_NODE" in node.sn_options:
            code += normalize_indents(node.code) + "\n"

    if bpy.context.scene.sna.addon.build_with_production_code:
        code = autopep8.fix_code(code)
    return code
