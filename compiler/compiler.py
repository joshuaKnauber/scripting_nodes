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
    __write_blockcomment(txt, "REGISTER ADDON")
    __write_in_text(txt, __create_register_function(addon_tree))
    __write_blockcomment(txt, "UNREGISTER ADDON")
    __write_in_text(txt, __create_unregister_function(addon_tree))
    
    module = txt.as_module()
    addons.append({ "text": txt, "module": module, "addon_tree": addon_tree })
    return __register_module(module)


def addon_is_registered(addon_tree):
    for addon in addons:
        if addon["addon_tree"] == addon_tree:
            return True
    return False
    
    
def handle_file_load():
    pass


def handle_file_unload():
    for addon in addons:
        __remove_addon(addon)
        
        
def remove_addon(addon_tree):
    for addon in addons:
        if addon["addon_tree"] == addon_tree:
            __remove_addon(addon)
            break
    
    
def __register_module(module):
    module.register()
    return True


def __remove_addon(addon):
    __unregister_module(addon["module"])
    bpy.data.texts.remove(addon["text"])
    addon["addon_tree"].has_changes = True
    addons.remove(addon)
    
    
def __unregister_module(module):
    module.unregister()


def __create_text_file(name):
    return bpy.data.texts.new(name)


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
    "version": "({str(graph.version[0])+", "+str(graph.version[1])+", "+str(graph.version[2])})",
    "blender": "({str(graph.blender[0])+", "+str(graph.blender[1])+", "+str(graph.blender[2])})",
    "location": "{graph.location}",
    "warning": "{graph.warning}",
    "wiki_url": "{graph.wiki_url}",
    "tracker_url": "{graph.tracker_url}",
    "category": "{graph.category if graph.category!="CUSTOM" else graph.custom_category}"
}}
"""


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