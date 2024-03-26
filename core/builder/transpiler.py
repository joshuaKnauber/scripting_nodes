import bpy

from ..utils.sockets import get_next_sockets
from ...utils.code import indent_code, minimize_indents
from ...utils.libraries import autopep8


def ntree_is_function(ntree: bpy.types.NodeTree):
    """Returns if the given node tree is a function"""
    for node in ntree.nodes:
        if node.bl_idname == "NodeGroupInput":
            return True
    return False


def ntree_to_code(ntree: bpy.types.NodeTree):
    """Converts the given node tree to a single code file"""
    imports = set(["import bpy"])
    global_code = []
    code = []
    register = []
    unregister = []

    for node in ntree.nodes:
        if getattr(node, "is_sn_node", False):
            if node.code_global:
                global_code.append(node.code_global)
            if node.code_imports:
                imports |= set(node.code_imports.split("\n"))
            if node.require_register:  # TODO
                code.append(node.code)
                if node.code_register:
                    register.append(node.code_register)
                if node.code_unregister:
                    unregister.append(node.code_unregister)

    combined = _combine_code(global_code, code, register, unregister)
    combined_imports = ""
    for imp in imports:
        combined_imports += f"{imp}\n"
    combined = f"{combined_imports}\n{combined}"

    return autopep8.fix_code(combined)


def ntree_to_function(ntree: bpy.types.NodeTree):
    """Converts the given node tree to a function"""
    imports = set(["import bpy"])
    global_code = []
    code = []
    register = []
    unregister = []

    # find starting point
    group_input = None
    for node in ntree.nodes:
        if node.bl_idname == "NodeGroupInput":
            group_input = node
            break
    if not group_input:
        return ""

    for node in ntree.nodes:
        if getattr(node, "is_sn_node", False):
            if node.code_global:
                global_code.append(node.code_global)
            if node.code_imports:
                imports |= set(node.code_imports.split("\n"))
            if node.require_register:  # TODO
                if node.code_register:
                    register.append(node.code_register)
                if node.code_unregister:
                    unregister.append(node.code_unregister)

    for out in group_input.outputs:
        if getattr(out, "is_program", False):
            next = get_next_sockets(out)
            if next:
                code.append(out.get_code())
            break

    combined = _combine_code(global_code, code, register, unregister)
    combined_imports = ""
    for imp in imports:
        combined_imports += f"{imp}\n"

    inputs = ", ".join([inp.function_input_name for inp in [*group_input.outputs][:-1]])

    combined = f"def {ntree.function_name()}({inputs}):\n{indent_code(minimize_indents(combined), 1, False)}"
    combined = f"{combined_imports}\n{combined}"

    return autopep8.fix_code(combined)


def _combine_code(
    global_code: list[str],
    code: list[str],
    register: list[str],
    unregister: list[str],
):
    combined = ""
    for c in global_code:
        combined += minimize_indents(c) + "\n"
    for c in code:
        combined += minimize_indents(c) + "\n"
    if register:
        combined += "def register():\n"
        for reg in register:
            combined += indent_code(minimize_indents(reg), 1, False) + "\n"
    if unregister:
        combined += "def unregister():\n"
        for unreg in unregister:
            combined += indent_code(minimize_indents(unreg), 1, False) + "\n"

    return combined
