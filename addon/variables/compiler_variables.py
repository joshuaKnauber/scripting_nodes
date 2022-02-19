import bpy



def variable_register_code():
    code = ""
    for ntree in bpy.data.node_groups:
        if ntree.bl_idname == "ScriptingNodesTree":
            code += f"{ntree.python_name} = {{"
            for var in ntree.variables:
                code += f"'{var.python_name}': {var.var_default}, "
            code += "}\n"
    return code