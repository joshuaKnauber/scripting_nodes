from scripting_nodes.src.lib.libraries import autopep8
from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import sn_nodes
from scripting_nodes.src.lib.utils.code.format import normalize_indents
import bpy


def code_gen_node_tree(ntree):
    code = "import bpy\n\n"
    register_code = ""
    unregister_code = ""

    # global scope code
    for node in sn_nodes(ntree):
        if node.code_global:
            code += normalize_indents(node.code_global) + "\n"

    # root nodes
    for node in sn_nodes(ntree):
        if "ROOT_NODE" in node.sn_options:
            code += normalize_indents(node.code) + "\n"

    # collect register/unregister code from all nodes
    for node in sn_nodes(ntree):
        if node.code_register:
            register_code += normalize_indents(node.code_register) + "\n"
        if node.code_unregister:
            unregister_code += normalize_indents(node.code_unregister) + "\n"

    # add register function
    if register_code:
        code += f"\ndef register():\n"
        # indent register code
        for line in register_code.strip().split("\n"):
            code += f"    {line}\n"
    else:
        code += "\ndef register():\n    pass\n"

    # add unregister function
    if unregister_code:
        code += f"\ndef unregister():\n"
        # indent unregister code
        for line in unregister_code.strip().split("\n"):
            code += f"    {line}\n"
    else:
        code += "\ndef unregister():\n    pass\n"

    if bpy.context.scene.sna.addon.build_with_production_code:
        code = autopep8.fix_code(code)
    return code
