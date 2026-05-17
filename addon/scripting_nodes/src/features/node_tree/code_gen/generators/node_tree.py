from .....lib.utils.node_tree.scripting_node_trees import sn_nodes
from .....lib.utils.code.format import normalize_indents
import bpy


def _find_group_interface(ntree):
    """Return (group_input, group_output) nodes inside a group tree, if present."""
    group_input = None
    group_output = None
    for node in sn_nodes(ntree):
        if node.bl_idname == "SNA_Node_GroupInput" and group_input is None:
            group_input = node
        elif node.bl_idname == "SNA_Node_GroupOutput" and group_output is None:
            group_output = node
    return group_input, group_output


# Names from the caller's method-scope that get auto-pulled inside group
# functions so emitted bare references (self.layout, context.scene, ...)
# resolve. Caller passes `_locals=locals()`; the function copies these
# specific keys back into local variables so the body uses bare names.
_GROUP_CALLER_LOCALS = ("self", "context", "event", "dummy")


def _emit_group_function(ntree):
    """Emit `def {ntree.module_name}(params, _locals=None): body; return (...)`
    for a group tree.

    A trailing `_locals=None` parameter lets callers pass their own `locals()`
    so things like `self.layout` and `context.scene` resolve inside the group
    body. Callers should always pass `_locals=locals()`.
    """
    group_input, group_output = _find_group_interface(ntree)

    # Parameters from the Group Input node's items list
    params = (
        [item["name"] for item in group_input.get_items()] if group_input else []
    )
    params.append("_locals=None")

    # Body: traverse the program chain from Group Input's "Function" output
    if group_input and len(group_input.outputs) > 0:
        body_raw = group_input.outputs[0].eval("pass")
    else:
        body_raw = "pass"

    # Return statement: eval each Group Output input
    return_line = None
    if group_output:
        returns = []
        reserved = getattr(group_output, "reserved_count", 1)
        for i, item in enumerate(group_output.get_items()):
            socket_index = i + reserved
            if socket_index < len(group_output.inputs):
                returns.append(group_output.inputs[socket_index].eval("None"))
        if len(returns) == 1:
            return_line = f"return {returns[0]}"
        elif len(returns) > 1:
            return_line = f"return (" + ", ".join(returns) + ")"

    lines = [f"def {ntree.module_name}({', '.join(params)}):"]
    # Pull caller's method-scope names into our locals so bare references
    # like `self.layout` work inside the body
    lines.append("    _locals = _locals or {}")
    for name in _GROUP_CALLER_LOCALS:
        lines.append(f"    {name} = _locals.get({name!r})")
    body_normalized = normalize_indents(body_raw) or "pass"
    for line in body_normalized.split("\n"):
        lines.append(("    " + line) if line.strip() else "")
    if return_line:
        lines.append("    " + return_line)
    return "\n" + "\n".join(lines) + "\n"


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

    # root nodes (skipped naturally for group trees; they typically have none)
    for node in sn_nodes(ntree):
        if "ROOT_NODE" in node.sn_options:
            code += normalize_indents(node.code_module) + "\n"

    # group function (group trees only)
    if getattr(ntree, "is_group", False):
        code += _emit_group_function(ntree)

    # collect register/unregister code from all nodes
    for node in sn_nodes(ntree):
        if node.code_register:
            register_code += normalize_indents(node.code_register) + "\n"
        if node.code_unregister:
            unregister_code += normalize_indents(node.code_unregister) + "\n"

    # add register function
    if register_code:
        code += f"\ndef register():\n"
        for line in register_code.strip().split("\n"):
            code += f"    {line}\n"
    else:
        code += "\ndef register():\n    pass\n"

    # add unregister function
    if unregister_code:
        code += f"\ndef unregister():\n"
        for line in unregister_code.strip().split("\n"):
            code += f"    {line}\n"
    else:
        code += "\ndef unregister():\n    pass\n"

    try:
        import autopep8

        code = autopep8.fix_code(code, options={"aggressive": 1})
    except Exception as e:
        print(f"[SN] autopep8 formatting failed: {e}")
    return code
