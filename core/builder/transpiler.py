import bpy

from ..utils.sockets import get_next_sockets
from ...utils.code import indent_code, minimize_indents
from ...utils import autopep8


def ntree_is_function(ntree: bpy.types.NodeTree):
    """Returns if the given node tree is a function"""
    for node in ntree.nodes:
        if node.bl_idname == "NodeGroupInput":
            return True
    return False


def _combine_code(
    imports: list[str],
    global_code: list[str],
    code: list[str],
    register: list[str],
    unregister: list[str],
    fix: bool,
):
    combined = ""
    for imp in imports:
        combined += f"{imp}\n"
    for c in global_code:
        combined += minimize_indents(c) + "\n"
    for c in code:
        combined += minimize_indents(c) + "\n"
    if register:
        combined += "def register():\n"
        for reg in register:
            combined += indent_code(minimize_indents(reg), 1) + "\n"
    if unregister:
        combined += "def unregister():\n"
        for unreg in unregister:
            combined += indent_code(minimize_indents(unreg), 1) + "\n"

    return autopep8.fix_code(combined) if fix else combined


def ntree_to_code(ntree: bpy.types.NodeTree):
    """Converts the given node tree to a single code file"""
    imports = ["import bpy"]
    global_code = []
    code = []
    register = []
    unregister = []

    for node in ntree.nodes:
        if getattr(node, "is_sn_node", False):
            if node.code_global:
                global_code.append(node.code_global)
            if getattr(node, "is_sn_node", False) and node.require_register:  # TODO
                code.append(node.code)
                if node.code_register:
                    register.append(node.code_register)
                if node.code_unregister:
                    unregister.append(node.code_unregister)
            # TODO add function imports

    return _combine_code(imports, global_code, code, register, unregister, True)


def ntree_to_function(ntree: bpy.types.NodeTree):
    """Converts the given node tree to a function"""
    imports = ["import bpy"]
    global_code = []
    code = []
    register = []
    unregister = []

    # find starting point
    group_input = None
    for node in ntree.nodes:
        if node.bl_idname == "NodeGroupInput":
            group_input = node
    if not group_input:
        return ""

    for node in ntree.nodes:
        if getattr(node, "is_sn_node", False):
            if node.code_global:
                global_code.append(node.code_global)
            if getattr(node, "is_sn_node", False) and node.require_register:  # TODO
                if node.code_register:
                    register.append(node.code_register)
                if node.code_unregister:
                    unregister.append(node.code_unregister)

    for out in group_input.outputs:
        if getattr(out, "is_program", False):
            next = get_next_sockets(out)
            if next:
                code.append(out.get_code())

    return _combine_code(imports, global_code, code, register, unregister, False)
