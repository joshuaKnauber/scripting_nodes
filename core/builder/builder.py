import os
import re
import shutil
import sys
import time

import addon_utils
import bpy

from ...utils import logger
from . import transpiler


IS_PROD_BUILD = False  # This is True while a production build is running
LAST_PROD_MODULE = None  # This is the last module name used for a production build


def build_addon(base_dir: str = None, prod_build: bool = False, module: str = None):
    if not has_addon() or not module:
        return

    global IS_PROD_BUILD
    IS_PROD_BUILD = prod_build
    sn = bpy.context.scene.sna

    try:
        if module != dev_module():
            store_prod_module_name(module)

        if sn.last_build_was_prod != prod_build:
            reload_node_code()
            sn.last_build_was_prod = prod_build

        _prepare_addon_dir(_get_addons_dir() if not base_dir else base_dir, module)
        _reload_addon(module)
    except Exception as e:
        logger.error("Failed to build addon")
        logger.error(e)
    finally:
        IS_PROD_BUILD = False
        build_complete_msg(prod_build)


def reload_node_code():
    """Reloads the code for all nodes. Call this before switching from or too production mode"""
    for ntree in bpy.data.node_groups:
        if getattr(ntree, "is_sn_ntree", False):
            for node in ntree.nodes:
                if getattr(node, "is_sn_node", False):
                    node.mark_dirty()


def remove_addon(module: str):
    remove_prod_module_name(module)
    addon_dir = get_addon_dir(_get_addons_dir(), module)
    if not os.path.exists(addon_dir):
        return

    _unregister_modules(module)
    _reset_addon_dir(_get_addons_dir(), module)
    shutil.rmtree(get_addon_dir(_get_addons_dir(), module))
    addon_utils.modules_refresh()


def _reload_addon(module: str):
    t1 = time.time()
    _unregister_modules(module)
    addon_utils.enable(module, default_set=True, persistent=True)
    logger.info(f"Addon reloaded in {round(time.time() - t1, 4)}s")


def has_module(module: str):
    for mod in addon_utils.modules():
        if mod.__name__ == module:
            return True
    return False


def persisted_modules_path():
    return os.path.join(os.path.dirname(__file__), "persisted_modules.txt")


def store_prod_module_name(module: str):
    modules = get_stored_prod_modules()
    if module in modules:
        return
    with open(persisted_modules_path(), "a") as write_file:
        write_file.write(module + "\n")


def remove_prod_module_name(module: str):
    modules = get_stored_prod_modules()
    if module in modules:
        modules.remove(module)
    with open(persisted_modules_path(), "w") as write_file:
        for mod in modules:
            write_file.write(mod + "\n")


def get_stored_prod_modules():
    if not os.path.exists(persisted_modules_path()):
        return []
    with open(persisted_modules_path(), "r") as read_file:
        return [*filter(lambda l: l.strip() != "", read_file.read().split("\n"))]


def toggle_stored_prod_modules():
    for mod in get_stored_prod_modules():
        if mod != module(prod_name=True):
            enable_module(mod)
        else:
            disable_module(mod)


def set_last_prod_module(module: str | None):
    global LAST_PROD_MODULE
    LAST_PROD_MODULE = module


def build_complete_msg(prod_build: bool):
    bpy.context.workspace.status_text_set(
        "✔️ Build Complete" + " (Production)" if prod_build else " (Development)"
    )
    bpy.app.timers.register(
        lambda: bpy.context.workspace.status_text_set(None), first_interval=1.5
    )


def disable_module(module: str):
    if not has_module(module):
        return
    addon_utils.disable(module, default_set=True)


def enable_module(module: str):
    if not has_module(module):
        return
    addon_utils.enable(module, default_set=True, persistent=True)


def _unregister_modules(module: str):
    if not has_module(module):
        return
    addon_utils.disable(module)
    for name in list(sys.modules.keys()):
        if name.startswith(module):
            del sys.modules[name]


def has_addon():
    """Returns if the file contains a scripting nodes addon"""
    for ntree in bpy.data.node_groups:
        if getattr(ntree, "is_sn_ntree", False):
            return True
    return False


def _prepare_addon_dir(base_dir: str, module: str):
    _reset_addon_dir(base_dir, module)
    _add_dir_structure(base_dir, module)
    _add_base_files(base_dir, module)
    for ntree in bpy.data.node_groups:
        if getattr(ntree, "is_sn_ntree", False):
            _add_node_tree(base_dir, module, ntree)


def _add_node_tree(base_dir: str, module: str, ntree: bpy.types.NodeTree):
    """Adds the given node tree to the given directory"""
    with open(
        os.path.join(_get_ntree_dir(base_dir, module), f"{ntree.module_name()}.py"), "w"
    ) as write_file:
        if transpiler.ntree_is_function(ntree):
            write_file.write(transpiler.ntree_to_function(ntree))
        else:
            write_file.write(transpiler.ntree_to_code(ntree))


def _add_base_files(base_dir: str, module: str):
    """Adds the base files to the addon directory"""
    sna = bpy.context.scene.sna
    basedir = get_addon_dir(base_dir, module)
    # add init file
    with open(os.path.join(basedir, "__init__.py"), "w") as write_file:
        with open(
            os.path.join(os.path.dirname(__file__), "templates", "init.txt"), "r"
        ) as read_file:
            text = read_file.read()
            if IS_PROD_BUILD:
                text = text.replace("$NAME", sna.info.name)
            else:
                text = text.replace("$NAME", f"{sna.info.name} (Development)")
            text = text.replace("$AUTHOR", sna.info.author)
            text = text.replace("$DESCRIPTION", sna.info.description)
            version = (
                f"({sna.info.version[0]}, {sna.info.version[1]}, {sna.info.version[2]})"
            )
            text = text.replace("$VERSION", version)
            blender = (
                f"({sna.info.blender[0]}, {sna.info.blender[1]}, {sna.info.blender[2]})"
            )
            text = text.replace("$BLENDER", blender)
            text = text.replace("$LOCATION", sna.info.location)
            category = (
                sna.info.custom_category
                if sna.info.category == "CUSTOM"
                else sna.info.category
            )
            text = text.replace("$CATEGORY", category)
            text = text.replace("$WARNING", sna.info.warning)
            text = text.replace("$DOC_URL", sna.info.doc_url)
            text = text.replace("$TRACKER_URL", sna.info.tracker_url)
            write_file.write(text)
    # add auto load file
    with open(os.path.join(basedir, "auto_load.py"), "w") as write_file:
        with open(
            os.path.join(os.path.dirname(__file__), "templates", "auto_load.txt"), "r"
        ) as read_file:
            write_file.write(read_file.read())


def _add_dir_structure(base_dir: str, module: str):
    """Adds the directory structure to the addon directory"""
    # add addon directory
    os.mkdir(_get_ntree_dir(base_dir, module))
    with open(
        os.path.join(_get_ntree_dir(base_dir, module), "__init__.py"), "w"
    ) as write_file:
        write_file.write("")
    # add assets directory
    os.mkdir(_get_assets_dir(base_dir, module))
    # add icons directory
    os.mkdir(_get_icon_dir(base_dir, module))


def _get_ntree_dir(base_dir: str, module: str):
    """Returns the directory for the given node tree"""
    return os.path.join(get_addon_dir(base_dir, module), "addon")


def _get_assets_dir(base_dir: str, module: str):
    """Returns the directory for the given node tree"""
    return os.path.join(get_addon_dir(base_dir, module), "assets")


def _get_icon_dir(base_dir: str, module: str):
    """Returns the directory for the given node tree"""
    return os.path.join(get_addon_dir(base_dir, module), "icons")


def _reset_addon_dir(base_dir: str, module: str):
    """Removes the current files and adds the addon directory"""
    addon_dir = get_addon_dir(base_dir, module)
    if os.path.exists(addon_dir):
        for filename in os.listdir(addon_dir):
            if os.path.isfile(os.path.join(addon_dir, filename)):
                os.remove(os.path.join(addon_dir, filename))
            else:
                shutil.rmtree(os.path.join(addon_dir, filename))
    else:
        os.mkdir(addon_dir)


def get_addon_dir(base_dir: str, module: str):
    """Returns the addon directory"""
    return os.path.join(base_dir, module)


def _get_addons_dir():
    """Returns the addons directory"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def dev_module():
    """Returns the module name for this addon in development mode"""
    return "scripting_nodes_dev"


def module(prod_name: bool = None):
    """Returns the module name for this addon"""
    if not prod_name:
        return dev_module()
    return bpy.context.scene.sna.info.module_name
