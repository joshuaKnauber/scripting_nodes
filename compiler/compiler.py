import bpy
from time import time
from .txt_blocks import license_block, serpens_functions


addons = []


def compile_addon(addon_tree):
    txt = None
    try:
        start_time = time()
        
        # get and/or create addon data
        addon_data = __find_compiled_addon(addon_tree)
        remove_addon(addon_tree)
        txt = __create_text_file(addon_tree.sn_graphs[0].name)
        addon_data["text"] = txt
        
        # add license block
        if not "license_block" in addon_data["code"]:
            addon_data["code"]["license_block"] = __get_license_block()
        
        # add addon info
        addon_data["code"]["addon_info"] = __normalize_code(__create_addon_info(addon_tree), 0)
        
        # add serpens functions
        if not "serpens_functions" in addon_data["code"]:
            addon_data["code"]["serpens_functions"] = __normalize_code(__get_serpens_functions(addon_tree), 0)

        # add graph code placeholder
        if not "graph_code" in addon_data["code"]:
            addon_data["code"]["graph_code"] = {}

        # collect existing did once lists
        addon_did_once = {} 
        for graph in addon_tree.sn_graphs:
            if not graph.node_tree.has_changes and graph.name in addon_data["code"]["graph_code"]:
                addon_did_once = {**addon_did_once, **addon_data["code"]["graph_code"][graph.name]["did_once"]}
        
        # go through all graphs
        new_graph_code = {}
        for graph in addon_tree.sn_graphs:
            if graph.node_tree.has_changes or not graph.name in addon_data["code"]["graph_code"]:

                # make graph code
                graph_code, graph_did_once              = __evaluate_graph(graph, addon_tree, addon_did_once)
                new_graph_code[graph.name]              = graph_code
                new_graph_code[graph.name]["did_once"]  = graph_did_once
                addon_did_once                          = {**addon_did_once, **graph_did_once}
                graph.node_tree.has_changes             = False

            else:
                # add unchanged graph code
                new_graph_code[graph.name] = addon_data["code"]["graph_code"][graph.name]

        # add the graphs code
        addon_data["code"]["graph_code"] = new_graph_code
        
        
        # write license and addon info
        __write_in_text(addon_data["text"], addon_data["code"]["license_block"])
        __write_paragraphs(addon_data["text"], 2)
        __write_in_text(addon_data["text"], addon_data["code"]["addon_info"])
        
        # write imports
        __write_blockcomment(addon_data["text"], "IMPORTS")
        __write_in_text(addon_data["text"], "import bpy")
        __write_in_text(addon_data["text"], "import os")
        for graph in addon_data["code"]["graph_code"]:
            if addon_data["code"]["graph_code"][graph]["imports"]:
                __write_graphcomment(addon_data["text"], graph)
                __write_in_text(addon_data["text"], addon_data["code"]["graph_code"][graph]["imports"])
                
        # write serpens functions
        __write_blockcomment(addon_data["text"], "SERPENS FUNCTIONS")
        __write_in_text(addon_data["text"], addon_data["code"]["serpens_functions"])
            
        # write imperative code
        __write_blockcomment(addon_data["text"], "IMPERATIVE CODE")
        for graph in addon_data["code"]["graph_code"]:
            if addon_data["code"]["graph_code"][graph]["imperative"]:
                __write_graphcomment(addon_data["text"], graph)
                __write_in_text(addon_data["text"], addon_data["code"]["graph_code"][graph]["imperative"])
            
        # write evaluated nodes
        __write_blockcomment(addon_data["text"], "EVALUATED CODE")
        for graph in addon_data["code"]["graph_code"]:
            if addon_data["code"]["graph_code"][graph]["evaluated"]:
                __write_graphcomment(addon_data["text"], graph)
                __write_in_text(addon_data["text"], addon_data["code"]["graph_code"][graph]["evaluated"])
        
        # write register function
        __write_blockcomment(addon_data["text"], "REGISTER ICONS")
        __write_in_text(addon_data["text"], __normalize_code(__create_icon_register(addon_tree),0))

        __write_blockcomment(addon_data["text"], "REGISTER ADDON")
        __write_in_text(addon_data["text"], "def register():")
        __write_in_text(addon_data["text"], "    \"\"\" registers this addon \"\"\"")
        __write_in_text(addon_data["text"], "    sn_register_icons()")
        for graph in addon_data["code"]["graph_code"]:
            if addon_data["code"]["graph_code"][graph]["register"]:
                __write_graphcomment(addon_data["text"], graph, 1)
                __write_in_text(addon_data["text"], __normalize_code(addon_data["code"]["graph_code"][graph]["register"],1))
        
        # write unregister function
        __write_blockcomment(addon_data["text"], "UNREGISTER ADDON")
        __write_in_text(addon_data["text"], "def unregister():")
        __write_in_text(addon_data["text"], "    \"\"\" removes this addon \"\"\"")
        __write_in_text(addon_data["text"], "    sn_unregister_icons()")
        for graph in addon_data["code"]["graph_code"]:
            if addon_data["code"]["graph_code"][graph]["unregister"]:
                __write_graphcomment(addon_data["text"], graph, 1)
                __write_in_text(addon_data["text"], __normalize_code(addon_data["code"]["graph_code"][graph]["unregister"],1))
        
        # make module
        module = addon_data["text"].as_module()
        addon_data["module"] = module
        addons.append(addon_data)

        # save time
        end_time = time()
        addon_tree.sn_graphs[0].last_compile_time = str(round(end_time-start_time,4))+"s"

        # register module
        success = __register_module(module)
        if success == True:
            return success
        else:
            raise success
        
        # redraw
        if context.screen:
            for a in bpy.context.screen.areas:
                a.tag_redraw()
    
    except Exception as exc:
        addon_prefs = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences
        if txt and addon_prefs.keep_after_error:
            bpy.data.texts.remove(txt)
        print("# # # # # # # # # ERROR WHILE COMPILING # # # # # # # # #")
        print(exc)
        print("# # # # # # # # # # # # # # # # # # # # # # # # # # # # #")
        return False
    
    
def compile_export(addon_tree):
    if compile_addon(addon_tree):
        return addons[-1]["text"]
    return False


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
            tree.sn_graphs[0].errors.clear()
            if tree.sn_graphs[0].compile_on_start:
                compile_addon(tree)


def handle_file_unload():
    for addon in addons:
        __unregister_module(addon["module"])

        
def remove_addon(addon_tree):
    for addon in addons:
        if addon["addon_tree"] == addon_tree:
            addon["addon_tree"].sn_graphs[0].errors.clear()
            __remove_addon(addon)
            break


def __find_compiled_addon(addon_tree):
    for addon in addons:
        if addon["addon_tree"] == addon_tree:
            edit_addon = addon
            return edit_addon
    return { "text": None, "code": {}, "module": None, "addon_tree": addon_tree }
    
    
def __register_module(module):
    try:
        module.register()
        return True
    except Exception as exc:
        return exc


def __remove_addon(addon):
    __unregister_module(addon["module"])
    bpy.data.texts.remove(addon["text"])
    addons.remove(addon)
    
    
def __unregister_module(module):
    if module:
        module.unregister()


def __create_text_file(name):
    addon_prefs = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences
    if addon_prefs.show_txt:
        txt = bpy.data.texts.new(name)
    else:
        txt = bpy.data.texts.new("."+name)
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


def __write_graphcomment(txt_file,text,indents=0):
    __write_paragraphs(txt_file, 1)
    txt_file.write(" "*indents*4 + "#######   " + text)
    __write_paragraphs(txt_file, 1)
    
    
def __get_license_block():
    return license_block()


def __get_serpens_functions(addon_tree):
    return serpens_functions(addon_tree)


def __create_icon_register(addon_tree):
    icon_list = ""
    img_list = ""
    for icon in addon_tree.sn_icons:
        icon_list += icon.name
        if icon.image and icon.image in bpy.data.images:
            img_list += icon.image
    return f"""
            def sn_register_icons():
                if not sn_is_dev():
                    icons = [{icon_list}]
                    bpy.types.Scene.{addon_tree.sn_graphs[0].short()}_icons = bpy.utils.previews.new()
                
                    icons_dir = os.path.join( os.path.dirname( __file__ ), "icons" )
                    for icon in icons:
                        bpy.types.Scene.{addon_tree.sn_graphs[0].short()}_icons.load( icon, os.path.join( icons_dir, icon + ".png" ), 'IMAGE' )
                else:
                    icons = [{img_list}]
                    bpy.types.Scene.{addon_tree.sn_graphs[0].short()}_icons = {{}}
                    
                    for icon in icons:
                        bpy.types.Scene.{addon_tree.sn_graphs[0].short()}_icons[icon] = {{"icon_id":99}}
                    
            def sn_unregister_icons():
                if not sn_is_dev():
                    bpy.utils.previews.remove( bpy.types.Scene.{addon_tree.sn_graphs[0].short()}_icons )
            """


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
    if new_code:
        if new_code[-1].isspace() or not new_code[-1]:
            new_code = new_code[:-1]
    return "\n".join(new_code)


def combine_blocks(block_list, indents):
    return __normalize_code("".join(block_list), indents)[indents*4:]


def process_node(node, touched_socket, indents=0):
    node_result = node.code_evaluate(bpy.context, bpy.context.scene.sn.addon_tree(), touched_socket)
    node_code = __normalize_code(node_result["code"], indents)
    return node_code


def process_returned(node, node_result):
    if node_result:
        if "code" in node_result:
            return __normalize_code(node_result["code"], 0)
    return ""


def __should_evaluate(node, evaluated_list):
    if "starts_tree" in node.node_options and node.node_options["starts_tree"]:
        if not "evaluate_once" in node.node_options or not node.node_options["evaluate_once"]:
            return True
        elif not node.bl_idname in evaluated_list:
            return True
    return False


def __should_import(node, imported_list):
    if not "import_once" in node.node_options or not node.node_options["import_once"]:
        return True
    elif not node.bl_idname in imported_list:
        return True
    return False


def __should_register(node, registered_list):
    if not "register_once" in node.node_options or not node.node_options["register_once"]:
        return True
    elif not node.bl_idname in registered_list:
        return True
    return False


def __should_unregister(node, unregistered_list):
    if not "unregister_once" in node.node_options or not node.node_options["unregister_once"]:
        return True
    elif not node.bl_idname in unregistered_list:
        return True
    return False


def __should_imperative(node, imperative_list):
    if not "imperative_once" in node.node_options or not node.node_options["imperative_once"]:
        return True
    elif not node.bl_idname in imperative_list:
        return True
    return False


def __evaluate_graph(graph, addon_tree, addon_did_once):
    graph_code = { "imports":"", "imperative":"", "evaluated":"", "register":"", "unregister":"" }
    graph_did_once = { "imports":[], "imperative":[], "evaluated":[], "register":[], "unregister":[] }

    for node in graph.node_tree.nodes:
        
        if __should_evaluate(node, {**addon_did_once, **graph_did_once}["evaluated"]):
            graph_code["evaluated"] += process_node(node, None)
            if not node.bl_idname in graph_did_once["evaluated"]: graph_did_once["evaluated"].append(node.bl_idname)
        
        if __should_import(node, {**addon_did_once, **graph_did_once}["imports"]):
            graph_code["imports"] += process_returned(node, node.code_imports(bpy.context, addon_tree))
            if not node.bl_idname in graph_did_once["imports"]: graph_did_once["imports"].append(node.bl_idname)
            
        if __should_imperative(node, {**addon_did_once, **graph_did_once}["imperative"]):
            graph_code["imperative"] += process_returned(node, node.code_imperative(bpy.context, addon_tree))
            if not node.bl_idname in graph_did_once["imperative"]: graph_did_once["imperative"].append(node.bl_idname)
            
        if __should_register(node, {**addon_did_once, **graph_did_once}["register"]):
            graph_code["register"] += process_returned(node, node.code_register(bpy.context, addon_tree))
            if not node.bl_idname in graph_did_once["register"]: graph_did_once["register"].append(node.bl_idname)
            
        if __should_unregister(node, {**addon_did_once, **graph_did_once}["unregister"]):
            graph_code["unregister"] += process_returned(node, node.code_unregister(bpy.context, addon_tree))
            if not node.bl_idname in graph_did_once["unregister"]: graph_did_once["unregister"].append(node.bl_idname)
            
    return graph_code, graph_did_once