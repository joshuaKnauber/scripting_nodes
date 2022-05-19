import bpy
import time
from ..utils import indent_code
from ..node_tree.sockets.conversions import CONVERT_UTILS
from ..addon.properties.compiler_properties import property_imperative_code, property_register_code, property_unregister_code
from ..addon.variables.compiler_variables import variable_register_code



def unregister_addon():
    """ Unregisters this addon """
    sn = bpy.context.scene.sn
    t1 = time.time()
    if sn.addon_unregister:
        try:
            sn.addon_unregister[0]()
        except Exception as error:
            print("error when unregister:", error)
        sn.addon_unregister.clear()
    if sn.debug_compile_time: print(f"---\nUnregister took {round((time.time()-t1)*1000, 2)}ms")



def compile_addon():
    """ Reregisters the current addon code and stores results """
    if not bpy.context.scene.sn.pause_reregister:
        t1 = time.time()
        sn = bpy.context.scene.sn

        # Unregister previous version
        unregister_addon()
                        
        # create text file
        txt = bpy.data.texts.new("tmp_serpens")
        txt.use_fake_user = False
        
        t2 = time.time()
        code = format_single_file()
        code += "\nbpy.context.scene.sn.addon_unregister.append(unregister)"
        code += "\nregister()"
        if sn.debug_compile_time: print(f"Generating code took {round((time.time()-t2)*1000, 2)}ms")
        txt.write(code)
        
        if sn.debug_code:
            if not "serpens_code_log" in bpy.data.texts:
                log = bpy.data.texts.new("serpens_code_log")
            log = bpy.data.texts["serpens_code_log"]
            log.clear()
            log.write(code)
            

        # run text file
        t2 = time.time()
        ctx = bpy.context.copy()
        ctx['edit_text'] = txt
        try:
            # exec(txt.as_string())
            bpy.ops.text.run_script(ctx)
        except Exception:
            print("^ ERROR WHEN REGISTERING SERPENS ADDON ^\n")
            if bpy.context.preferences.addons[__name__.partition('.')[0]].preferences.keep_last_error_file:
                if not "serpens_error" in bpy.data.texts:
                    bpy.data.texts.new("serpens_error")
                err = bpy.data.texts["serpens_error"]
                err.clear()
                err.write(code)
        if sn.debug_compile_time: print(f"Register took {round((time.time()-t2)*1000, 2)}ms\n---")

        # remove text file
        bpy.data.texts.remove(txt)
        sn.compile_time = time.time() - t1


LICENSE = """
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

DEFAULT_IMPORTS = """
import bpy
import bpy.utils.previews
"""

GLOBAL_VARS = """
addon_keymaps = {}
_icons = None
"""

REGISTER = """
global _icons
_icons = bpy.utils.previews.new()
"""

UNREGISTER = """
global _icons
bpy.utils.previews.remove(_icons)

wm = bpy.context.window_manager
kc = wm.keyconfigs.addon
for km, kmi in addon_keymaps.values():
    km.keymap_items.remove(kmi)
addon_keymaps.clear()
"""

def format_single_file():
    """ Returns the entire addon code (for development) formatted for a single python file """
    sn = bpy.context.scene.sn
    imports, imperative, main, register, unregister = (DEFAULT_IMPORTS, CONVERT_UTILS + GLOBAL_VARS, "", REGISTER, UNREGISTER)

    # add property and variable code
    t1 = time.time()
    imperative += variable_register_code() + "\n"
    t2 = time.time()
    register += property_register_code() + "\n"
    t3 = time.time()
    unregister += property_unregister_code() + "\n"
    t4 = time.time()
    
    # add node code
    for node in get_trigger_nodes():
        if node.code_import and not node.code_import in imports: imports += "\n" + node.code_import
        if node.code_imperative and not node.code_imperative in imperative: imperative += "\n" + node.code_imperative
        if node.code: main += "\n" + node.code
        if node.code_register: register += "\n" + node.code_register
        if node.code_unregister: unregister += "\n" + node.code_unregister
    t5 = time.time()
    
    # add property code
    main += "\n" + property_imperative_code() + "\n"
    t6 = time.time()

    # format register functions
    if not register.strip():
        register = "pass\n"
    if not unregister.strip():
        unregister = "pass\n"
    
    code = f"{LICENSE}\n{imports}\n{imperative}\n{main}\n\ndef register():\n{indent_code(register, 1, 0)}\n\ndef unregister():\n{indent_code(unregister, 1, 0)}\n\n"
    t7 = time.time()
    
    if (sn.remove_duplicate_code and sn.debug_code) or sn.is_exporting:
        code = remove_duplicates(code)
    t8 = time.time()
    
    if (sn.format_code and sn.debug_code) or sn.is_exporting:
        code = format_linebreaks(code)
    t9 = time.time()

    if sn.debug_compile_time:
        print(f"--Variable register code generation took {round((t2-t1)*1000, 2)}ms")
        print(f"--Property register code generation took {round((t3-t2)*1000, 2)}ms")
        print(f"--Property unregister code generation took {round((t4-t3)*1000, 2)}ms")
        print(f"--Node code generation took {round((t5-t4)*1000, 2)}ms")
        print(f"--Property imperative code generation took {round((t6-t5)*1000, 2)}ms")
        print(f"--Joining code took {round((t7-t6)*1000, 2)}ms")
        print(f"--Removing duplicate code took {round((t8-t7)*1000, 2)}ms")
        print(f"--Formatting linebreaks took {round((t9-t8)*1000, 2)}ms")
    return code


def remove_duplicates(code):
    code = remove_duplicate_functions(code)
    code = remove_duplicate_imports(code)
    return code


def remove_func(code, func):
    lines = code.split("\n")
    newLines = []
    inFunc = False
    for i, line in enumerate(lines):
        if inFunc and len(line) - len(line.lstrip()) == 0:
            inFunc = False
            newLines += lines[i:]
            break
        elif not inFunc:
            if len(line) > 3 and line[:3] == "def":
                if line[:len(f"def {func}(")] == f"def {func}(":
                    inFunc = True
                    break
            if not inFunc:
                newLines.append(line)
        elif inFunc:
            print(line)
    return "\n".join(newLines)


def remove_duplicate_functions(code):
    lines = code.split("\n")
    functions = []
    remove = []
    for line in lines:
        if len(line) > 3 and line[:3] == "def":
            func = line.split("(")[0].split(" ")[-1]
            if func in functions or code.count(func) == 1:
                remove.append(func)
            else:
                functions.append(func)

    newLines = []
    inFunc = False
    for line in lines:
        if inFunc and len(line) - len(line.lstrip()) == 0:
            inFunc = False
        if not inFunc:
            if len(line) > 3 and line[:3] == "def" and "(" in line:
                for func in remove:
                    if line.split("(")[0] == f"def {func}":
                        remove.remove(func)
                        inFunc = True
                        break
            if not inFunc:
                newLines.append(line)
    return "\n".join(newLines)


def remove_duplicate_imports(code):
    imports = []
    newLines = []
    for line in code.split("\n"):
        if line[:6] == "import" or (line[:4] == "from" and "import" in line):
            if not line.strip() in imports:
                imports.append(line.strip())
                newLines.append(line)
        else:
            newLines.append(line)
    return "\n".join(newLines)


def format_linebreaks(code):
    lines = code.split("\n")
    newLines = []
    for i, line in enumerate(lines):
        if line.strip():
            # insert linebreaks for lines with no indent
            if len(line) - len(line.lstrip()) == 0:
                # linebreak for going from indents to no indents
                if newLines and len(newLines[-1]) - len(newLines[-1].lstrip()) > 0:
                    newLines.append("\n")
                # linebreak for imperative functions
                elif newLines and len(line) > 3 and len(newLines[-1].strip()) and line[:3] == "def" and not newLines[-1][0] == "@":
                    newLines.append("\n")
                # linebreak for imperative functions
                elif newLines and "import" in line and not "import" in newLines[-1]:
                    newLines.append("\n")
            # insert linebreaks for lines with indent
            elif newLines:
                # linebreak for decorated functions in classes
                if line and line.lstrip()[0] == "@":
                    newLines.append("")
                # linebreak for functions without decorator
                elif len(line) > 3 and len(newLines[-1].strip()) and line.lstrip()[:3] == "def" and not newLines[-1].lstrip()[0] == "@":
                    newLines.append("")
            newLines.append(line)
    return "\n".join(newLines) + "\n"
    
    
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