import bpy
from .txt_blocks import license_block, serpens_functions


addons = []


def compile_addon(addon_tree):
    addon_data = __find_compiled_addon(addon_tree)
    remove_addon(addon_tree)
    txt = __create_text_file(addon_tree.sn_graphs[0].name)
    addon_data["text"] = txt
    
    # add license block
    if not "license_block" in addon_data["code"]:
        addon_data["code"]["license_block"] = __get_license_block()
    
    # add addon info
    addon_data["code"]["addon_info"] = __create_addon_info(addon_tree)

    # add graph code placeholder
    if not "graph_code" in addon_data["code"]:
        addon_data["code"]["graph_code"] = {}

    # go through all graphs
    new_graph_code = {}
    for graph in addon_tree.sn_graphs:
        if graph.node_tree.has_changes or not graph.name in addon_data["code"]["graph_code"]:

            # make graph code
            new_graph_code[graph.name] = __evaluate_graph(graph, addon_tree)

        else:
            new_graph_code[graph.name] = addon_data["code"]["graph_code"][graph.name]
    
    # add the graph code
    addon_data["code"]["graph_code"] = new_graph_code
    
    
    __write_in_text(addon_data["text"], addon_data["code"]["license_block"])
    __write_paragraphs(addon_data["text"], 2)
    __write_in_text(addon_data["text"], addon_data["code"]["addon_info"])
    
    __write_blockcomment(addon_data["text"], "IMPORTS")
    for graph in addon_data["code"]["graph_code"]:
        if addon_data["code"]["graph_code"][graph]["imports"]:
            __write_graphcomment(addon_data["text"], graph)
            __write_in_text(addon_data["text"], addon_data["code"]["graph_code"][graph]["imports"])
        
    __write_blockcomment(addon_data["text"], "EVALUATED CODE")
    for graph in addon_data["code"]["graph_code"]:
        if addon_data["code"]["graph_code"][graph]["evaluated"]:
            __write_graphcomment(addon_data["text"], graph)
            __write_in_text(addon_data["text"], addon_data["code"]["graph_code"][graph]["evaluated"])
        
    __write_blockcomment(addon_data["text"], "REGISTER ADDON")
    for graph in addon_data["code"]["graph_code"]:
        if addon_data["code"]["graph_code"][graph]["register"]:
            __write_graphcomment(addon_data["text"], graph)
            __write_in_text(addon_data["text"], addon_data["code"]["graph_code"][graph]["register"])
        
    __write_blockcomment(addon_data["text"], "UNREGISTER ADDON")
    for graph in addon_data["code"]["graph_code"]:
        if addon_data["code"]["graph_code"][graph]["unregister"]:
            __write_graphcomment(addon_data["text"], graph)
            __write_in_text(addon_data["text"], addon_data["code"]["graph_code"][graph]["unregister"])
    
    # __write_in_text(txt, __create_addon_info(addon_tree))
    # __write_blockcomment(txt, "SERPENS FUNCTIONS")
    # __write_in_text(txt, __get_serpens_functions())
    
    
    # for graph in addon_tree.sn_graphs:
    #     if graph.node_tree.has_changes:
    #         graph.node_tree.set_changes(False)
    # print("compiled")

    
    module = addon_data["text"].as_module()
    addon_data["module"] = module
    addons.append(addon_data)

    return __register_module(module)


def __find_compiled_addon(addon_tree):
    for addon in addons:
        if addon["addon_tree"] == addon_tree:
            edit_addon = addon
            return edit_addon
    return { "text": None, "code": {}, "module": None, "addon_tree": addon_tree }


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
    # if module:
    #     module.unregister()
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


def __write_graphcomment(txt_file,text):
    __write_paragraphs(txt_file, 1)
    txt_file.write("#######   " + text)
    __write_paragraphs(txt_file, 1)
    
    
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
    graph_code = { "imports":"", "imperative":"", "evaluated":"", "register":"", "unregister":"" }
    for node in graph.node_tree.nodes:
        
        if node.node_options["starts_tree"]:
            graph_code["evaluated"] += process_node(node, None)
    return graph_code