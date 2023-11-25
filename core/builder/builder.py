import os
import re
import shutil
import sys
import time

import addon_utils
import bpy

from ...utils import logger
from ...utils.code import normalize_indents
from ...utils import autopep8


def build_addon(base_dir: str = None) -> str:
    if not base_dir:
        base_dir = _get_addons_dir()
    if not _has_addon():
        return
    _prepare_addon_dir(base_dir)
    _reload_addon()
    return get_addon_dir(base_dir)


def _reload_addon():
    t1 = time.time()
    addon_utils.disable("test_addon")
    for name in list(sys.modules.keys()):
        if name.startswith("test_addon"):
            del sys.modules[name]
    addon_utils.enable("test_addon")
    logger.info(f"Addon reloaded in {round(time.time() - t1, 4)}s")


def _has_addon():
    """Returns if the file contains a scripting nodes addon"""
    for ntree in bpy.data.node_groups:
        if getattr(ntree, "is_sn_ntree", False):
            return True
    return False


def _prepare_addon_dir(base_dir: str):
    _reset_addon_dir(base_dir)
    _add_dir_structure(base_dir)
    _add_base_files(base_dir)
    for ntree in bpy.data.node_groups:
        if getattr(ntree, "is_sn_ntree", False):
            _add_node_tree(base_dir, ntree)


def _add_node_tree(base_dir: str, ntree: bpy.types.NodeTree):
    """Adds the given node tree to the given directory"""
    with open(
        os.path.join(_get_ntree_dir(base_dir), _get_ntree_filename(ntree)), "w"
    ) as write_file:
        write_file.write(_ntree_to_code(ntree))


def _get_ntree_filename(ntree: bpy.types.NodeTree):
    """Returns the filename for the given node tree"""
    pythonic = re.sub("\W|^(?=\d)", "_", ntree.name.lower())
    return f"{pythonic}.py"


def _add_base_files(base_dir: str):
    """Adds the base files to the addon directory"""
    sna = bpy.context.scene.sna
    basedir = get_addon_dir(base_dir)
    # add init file
    with open(os.path.join(basedir, "__init__.py"), "w") as write_file:
        with open(
            os.path.join(os.path.dirname(__file__), "templates", "init.txt"), "r"
        ) as read_file:
            text = read_file.read()
            text = text.replace("$NAME", sna.info.name)
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


def _ntree_to_code(ntree: bpy.types.NodeTree):
    """Converts the given node tree to code"""
    code = "import bpy\n\n"
    register = ""
    unregister = ""

    for node in ntree.nodes:
        if getattr(node, "is_sn_node", False) and node.require_register:  # TODO
            code += normalize_indents(node.code) + "\n"
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

    return autopep8.fix_code(code)


def _add_dir_structure(base_dir: str):
    """Adds the directory structure to the addon directory"""
    # add addon directory
    os.mkdir(_get_ntree_dir(base_dir))
    with open(os.path.join(_get_ntree_dir(base_dir), "__init__.py"), "w") as write_file:
        write_file.write("")
    # add assets directory
    os.mkdir(_get_assets_dir(base_dir))
    # add icons directory
    os.mkdir(_get_icon_dir(base_dir))


def _get_ntree_dir(base_dir: str):
    """Returns the directory for the given node tree"""
    return os.path.join(get_addon_dir(base_dir), "addon")


def _get_assets_dir(base_dir: str):
    """Returns the directory for the given node tree"""
    return os.path.join(get_addon_dir(base_dir), "assets")


def _get_icon_dir(base_dir: str):
    """Returns the directory for the given node tree"""
    return os.path.join(get_addon_dir(base_dir), "icons")


def _reset_addon_dir(base_dir: str):
    """Removes the current files and adds the addon directory"""
    addon_dir = get_addon_dir(base_dir)
    if os.path.exists(addon_dir):
        for filename in os.listdir(addon_dir):
            if os.path.isfile(os.path.join(addon_dir, filename)):
                os.remove(os.path.join(addon_dir, filename))
            else:
                shutil.rmtree(os.path.join(addon_dir, filename))
    else:
        os.mkdir(addon_dir)


def get_addon_dir(base_dir: str):
    """Returns the addon directory"""
    return os.path.join(base_dir, "test_addon")


def _get_addons_dir():
    """Returns the addons directory"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
