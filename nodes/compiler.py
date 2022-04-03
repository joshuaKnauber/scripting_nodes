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



DEFAULT_IMPORTS = """
import bpy
"""

GLOBAL_VARS = """
addon_keymaps = {}
"""

UNREGISTER_KEYMAPS = """
wm = bpy.context.window_manager
kc = wm.keyconfigs.addon
for km, kmi in addon_keymaps.values():
    km.keymap_items.remove(kmi)
addon_keymaps.clear()
"""

def format_single_file():
    """ Returns the entire addon code (for development) formatted for a single python file """
    sn = bpy.context.scene.sn
    imports, imperative, main, register, unregister = (DEFAULT_IMPORTS, CONVERT_UTILS + GLOBAL_VARS, "", "", UNREGISTER_KEYMAPS)

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
        if node.code_import: imports += "\n" + node.code_import
        if node.code_imperative: imperative += "\n" + node.code_imperative
        # TODO remove duplicates from import and imperative
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
    
    code = f"{imports}\n{imperative}\n{main}\n\ndef register():\n{indent_code(register, 1, 0)}\n\ndef unregister():\n{indent_code(unregister, 1, 0)}\n\n"
    t7 = time.time()

    if sn.debug_compile_time:
        print(f"--Variable register code generation took {round((t2-t1)*1000, 2)}ms")
        print(f"--Property register code generation took {round((t3-t2)*1000, 2)}ms")
        print(f"--Property unregister code generation took {round((t4-t3)*1000, 2)}ms")
        print(f"--Node code generation took {round((t5-t4)*1000, 2)}ms")
        print(f"--Property imperative code generation took {round((t6-t5)*1000, 2)}ms")
        print(f"--Code formatting took {round((t7-t6)*1000, 2)}ms")
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