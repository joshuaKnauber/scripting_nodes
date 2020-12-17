import bpy
from .txt_blocks import license_block, serpens_functions


addons = []



def compile_addon(addon_tree):
    remove_addon(addon_tree)
    txt = __create_text_file(addon_tree.sn_graphs[0].name)
    
    __write_in_text(txt, __get_license_block())
    __write_paragraphs(txt, 2)
    __write_in_text(txt, __create_addon_info(addon_tree))
    __write_blockcomment(txt, "SERPENS FUNCTIONS")
    __write_in_text(txt, __get_serpens_functions())
    __write_blockcomment(txt, "EVALUATED CODE")
    __write_in_text(txt, __create_evaluated(addon_tree))
    __write_blockcomment(txt, "REGISTER ADDON")
    __write_in_text(txt, __create_register_function(addon_tree))
    __write_blockcomment(txt, "UNREGISTER ADDON")
    __write_in_text(txt, __create_unregister_function(addon_tree))
    
    
    for graph in addon_tree.sn_graphs:
        if graph.node_tree.has_changes:
            graph.node_tree.set_changes(False)
    print("compiled")

    
    module = txt.as_module()
    addons.append({ "text": txt, "module": module, "addon_tree": addon_tree })

    return __register_module(module)


def addon_is_registered(addon_tree):
    for addon in addons:
        if addon["addon_tree"] == addon_tree:
            return True
    return False
    
    
def handle_file_load():
    for txt in bpy.data.texts:
        if txt.is_sn_addon:
            bpy.data.texts.remove(txt)
    for tree in bpy.data.node_groups:
        if len(tree.sn_graphs) > 0:
            bpy.app.timers.register(tree.run_autocompile, first_interval=0.1)
            if tree.sn_graphs[0].compile_on_start:
                compile_addon(tree)


def handle_file_unload():
    for addon in addons:
        __unregister_module(addon["module"])

        
def remove_addon(addon_tree):
    for addon in addons:
        if addon["addon_tree"] == addon_tree:
            __remove_addon(addon)
            break
    
    
def __register_module(module):
    # module.register()
    return True


def __remove_addon(addon):
    __unregister_module(addon["module"])
    bpy.data.texts.remove(addon["text"])
    addons.remove(addon)
    
    
def __unregister_module(module):
    # module.unregister()
    pass


def __create_text_file(name):
    txt = bpy.data.texts.new(name)
    txt.is_sn_addon = True
    return txt


def __write_in_text(txt_file,text):
    txt_file.write(text.strip("\n")+"\n")


def __write_paragraphs(txt_file,amount):
    for _ in range(amount+1):
        txt_file.write("\n")


def __write_blockcomment(txt_file,text):
    __write_paragraphs(txt_file, 2)
    txt_file.write("###############   " + text)
    __write_paragraphs(txt_file, 2)
    
    
def __get_license_block():
    return license_block()


def __get_serpens_functions():
    return serpens_functions()


def __create_addon_info(addon_tree):
    graph = addon_tree.sn_graphs[0]
    return f"""
bl_info = {{
    "name": "{graph.name}",
    "description": "{graph.description}",
    "author": "{graph.author}",
    "version": ({str(graph.version[0])+", "+str(graph.version[1])+", "+str(graph.version[2])}),
    "blender": ({str(graph.blender[0])+", "+str(graph.blender[1])+", "+str(graph.blender[2])}),
    "location": "{graph.location}",
    "warning": "{graph.warning}",
    "wiki_url": "{graph.wiki_url}",
    "tracker_url": "{graph.tracker_url}",
    "category": "{graph.category if graph.category!="CUSTOM" else graph.custom_category}"
}}
"""


def __normalize_code(code, indents):
    code = code.split("\n")
    remove_indents = 999
    for line in code:
        if not line.isspace() and line:
            amount_spaces = len(line) - len(line.lstrip())
            remove_indents = min(amount_spaces, remove_indents)
    new_code = []
    for line in code:
        if len(line) >= remove_indents:
            new_code.append( " "*indents*4 + line[remove_indents:] )
    if new_code and new_code[-1].isspace():
        new_code = new_code[:-1]
    return "\n".join(new_code)


def combine_blocks(block_list, indents):
    return __normalize_code("".join(block_list), indents)[indents*4:]


def process_node(node, touched_socket, indents=0):
    node_result = node.code_evaluate(bpy.context, bpy.context.scene.sn.addon_tree(), touched_socket)
    node_code = __normalize_code(node_result["code"], indents)
    return node_code


def __evaluate_graph(graph, addon_tree):
    graph_code = ""
    for node in graph.node_tree.nodes:
        if node.node_options["starts_tree"]:
            graph_code += process_node(node, None)
    return graph_code


def __create_evaluated(addon_tree):
    evaluated_code = ""
    for graph in addon_tree.sn_graphs:
        evaluated_code += __evaluate_graph(graph, addon_tree)
    return evaluated_code


def __create_register_function(addon_tree):
    return """
def register():
    pass
"""


def __create_unregister_function(addon_tree):
    return """
def unregister():
    pass
"""