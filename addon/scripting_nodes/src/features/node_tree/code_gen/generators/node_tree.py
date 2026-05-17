from .....lib.utils.node_tree.scripting_node_trees import sn_nodes
from .....lib.utils.code.format import normalize_indents
import bpy


def code_gen_node_tree(ntree):
    register_code = ""
    unregister_code = ""

    # imports (collected and deduplicated)
    import_lines = {"import bpy"}
    for node in sn_nodes(ntree):
        if node.code_imports:
            for line in normalize_indents(node.code_imports).split("\n"):
                stripped = line.strip()
                if stripped:
                    import_lines.add(stripped)
    code = "\n".join(sorted(import_lines)) + "\n\n"

    # global scope code
    for node in sn_nodes(ntree):
        if node.code_global:
            code += normalize_indents(node.code_global) + "\n"

    # root nodes
    for node in sn_nodes(ntree):
        if "ROOT_NODE" in node.sn_options:
            code += normalize_indents(node.code_module) + "\n"

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
        try:
            import autopep8

            code = autopep8.fix_code(code, options={"aggressive": 1})
        except Exception as e:
            print(f"[SN] autopep8 formatting failed: {e}")
    return code
