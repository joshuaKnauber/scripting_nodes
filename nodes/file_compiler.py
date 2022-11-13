import bpy
import os
import importlib
import threading
import time
import shutil
from ..utils import indent_code


"""

[] Figure out how to separate node trees into separate files
    - Could separate all trigger nodes into separate files? (at least panels, operators, ...)
    - Node trees are for editing, saved files are structured to best support importing without circular import errors

[] Figure out benefits of separate files
    - Forced to optimize generated code (better understandability)

[] Figure out potential inclusion of full custom files (IDE support)
    - Option to choose location to save addon -> Can be an existing folder
        - If it is not an existing folder create basic init file
        - Else load the data from the init file and add serpens hooks into register/unregister
    - Create serpens folder (generated/serpens/visual_scripting)

[] Figure out collaboration support
    - Introspection files for each generated file or one overall file for the entire addon or for each node tree
    - Goal is to make a change in the code files or in the serpens nodes
    - What is the end game here?
        - Do all people editing the addon have serpens / need to have serpens?
        - 

"""


ADDON_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def _reload_module(module_name):
    module = importlib.import_module(module_name)
    t1 = time.time()
    module.unregister()
    importlib.reload(module)
    module.register()
    t2 = time.time()
    # sn.compile_time = round((t2 - t1), 2)
    print("Reloaded in", t2 - t1, "seconds")

def compile_addon():
    if file_has_addon():
        sn = bpy.context.scene.sn

        code = format_single_file()
        module_dir = os.path.join(ADDON_DIR, sn.module_name)

        reload = True
        if not os.path.exists(module_dir):
            os.mkdir(module_dir)
            reload = False
        else:
            # clear folder
            for f in os.listdir(module_dir):
                if os.path.isfile(os.path.join(module_dir, f)):
                    os.remove(os.path.join(module_dir, f))
                else:
                    shutil.rmtree(os.path.join(module_dir, f))

        os.mkdir(os.path.join(module_dir, "assets"))
        os.mkdir(os.path.join(module_dir, "icons"))

        for node_tree in bpy.data.node_groups:
            if node_tree.bl_idname == "ScriptingNodesTree":
                with open(os.path.join(module_dir, f"{node_tree.python_name}.py"), "w") as f:
                    f.seek(0)
                    f.truncate()
                    f.write(f"# Generated from {node_tree.name}")

        with open(os.path.join(module_dir, f"__init__.py"), "w") as f:
            f.write(f"""
bl_info = {{
    "name": "{sn.addon_name}",
    "author": "{sn.author}",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "View3D",
    "description": "{sn.description}",
    "warning": "",
    "wiki_url": "",
    "category": "Development",
}}

def register():
    pass

def unregister():
    pass
            """)
        
        if reload:
            # threading.Thread(target=_reload_module, args=(sn.module_name,), daemon=True).start()
            _reload_module(sn.module_name)
        else:
            bpy.ops.preferences.addon_enable(module=sn.module_name)
            bpy.ops.preferences.addon_refresh()

        for area in bpy.context.screen.areas:
            area.tag_redraw()


def file_has_addon():
    for node_tree in bpy.data.node_groups:
        if node_tree.bl_idname == "ScriptingNodesTree":
            return True
    return False


def format_single_file():
    """ Returns the entire addon code (for development) formatted for a single python file """
    sn = bpy.context.scene.sn
    imports, imperative, main, register, unregister = ("", "", "", "", "")
    
    for node in get_trigger_nodes():
        if node.code_import and not node.code_import in imports: imports += "\n" + node.code_import
        if node.code_imperative and not node.code_imperative in imperative: imperative += "\n" + node.code_imperative
        if node.code: main += "\n" + node.code
        if node.code_register: register += "\n" + node.code_register
        if node.code_unregister: unregister += "\n" + node.code_unregister

    code = ""
    
    return code


def get_trigger_nodes():
    """ Returns a list of all trigger nodes in all node trees """
    nodes = []
    for ntree in bpy.data.node_groups:
        if ntree.bl_idname == "ScriptingNodesTree":
            for node in ntree.nodes:
                if getattr(node, "is_trigger", False):
                    nodes.append(node)
    nodes = sorted(nodes, key=lambda node: node.order)
    return nodes