import os
import re
import shutil
import sys
import threading
import time

import addon_utils
import bpy

from ...utils import logger


def build_addon():
    if not _has_addon():
        return
    _prepare_addon_dir()
    _reload_addon()


def _reload_addon():
    t1 = time.time()
    addon_utils.disable("test_addon")
    for name in list(sys.modules.keys()):
        if name.startswith("test_addon"):
            del sys.modules[name]
    addon_utils.enable("test_addon")
    logger.info(f"Addon reloaded in {round(time.time() - t1, 4)}s")


def _has_addon():
    """ Returns if the file contains a scripting nodes addon """
    for ntree in bpy.data.node_groups:
        if getattr(ntree, "is_sn", False):
            return True
    return False


def _prepare_addon_dir():
    _reset_addon_dir()
    _add_dir_structure()
    _add_base_files()
    for ntree in bpy.data.node_groups:
        if getattr(ntree, "is_sn", False):
            _add_node_tree(ntree)


def _add_node_tree(ntree: bpy.types.NodeTree):
    """ Adds the given node tree to the given directory """
    with open(os.path.join(_get_ntree_dir(), _get_ntree_filename(ntree)), "w") as write_file:
        write_file.write(_ntree_to_code(ntree))


def _get_ntree_filename(ntree: bpy.types.NodeTree):
    """ Returns the filename for the given node tree """
    pythonic = re.sub('\W|^(?=\d)', '_', ntree.name.lower())
    return f"{pythonic}.py"


def _add_base_files():
    """ Adds the base files to the addon directory """
    sn = bpy.context.scene.sn
    basedir = _get_addon_dir()
    # add init file
    with open(os.path.join(basedir, "__init__.py"), "w") as write_file:
        with open(os.path.join(os.path.dirname(__file__), "templates", "init.txt"), "r") as read_file:
            text = read_file.read()
            text = text.replace("$NAME", sn.info.name)
            text = text.replace("$DESCRIPTION", sn.info.description)
            write_file.write(text)
    # add auto load file
    with open(os.path.join(basedir, "auto_load.py"), "w") as write_file:
        with open(os.path.join(os.path.dirname(__file__), "templates", "auto_load.txt"), "r") as read_file:
            write_file.write(read_file.read())


def _ntree_to_code(ntree: bpy.types.NodeTree):
    """ Converts the given node tree to code """
    code = "import bpy\n\n"
    register = ""
    unregister = ""

    for node in ntree.nodes:
        if getattr(node, "is_sn", False) and node.require_register:  # TODO
            code += node.code + "\n"
            print(node, node.code_register)
            if node.code_register:
                register += "    " + node.code_register + "\n"
            if node.code_unregister:
                unregister += "    " + node.code_unregister + "\n"

    code += "\n"
    if register:
        code += "def register():\n"
        code += register + "\n"
    if unregister:
        code += "def unregister():\n"
        code += unregister + "\n"

    return code


def _add_dir_structure():
    """ Adds the directory structure to the addon directory """
    # add addon directory
    os.mkdir(_get_ntree_dir())
    with open(os.path.join(_get_ntree_dir(), "__init__.py"), "w") as write_file:
        write_file.write("")
    # add assets directory
    os.mkdir(_get_assets_dir())
    # add icons directory
    os.mkdir(_get_icon_dir())


def _get_ntree_dir():
    """ Returns the directory for the given node tree """
    return os.path.join(_get_addon_dir(), "addon")


def _get_assets_dir():
    """ Returns the directory for the given node tree """
    return os.path.join(_get_addon_dir(), "assets")


def _get_icon_dir():
    """ Returns the directory for the given node tree """
    return os.path.join(_get_addon_dir(), "icons")


def _reset_addon_dir():
    """ Removes the current files and adds the addon directory """
    addon_dir = _get_addon_dir()
    if os.path.exists(addon_dir):
        for filename in os.listdir(addon_dir):
            if os.path.isfile(os.path.join(addon_dir, filename)):
                os.remove(os.path.join(addon_dir, filename))
            else:
                shutil.rmtree(os.path.join(addon_dir, filename))
    else:
        os.mkdir(addon_dir)


def _get_addon_dir():
    """ Returns the addon directory """
    return os.path.join(_get_addons_dir(), "test_addon")


def _get_addons_dir():
    """ Returns the addons directory """
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
