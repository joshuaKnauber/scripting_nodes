from scripting_nodes.src.lib.utils.logger import log_if
from scripting_nodes.src.lib.constants.paths import ADDON_FOLDER
import addon_utils
import sys
import bpy
import time
import os


def reload_addon(module: str):
    """Reload an addon module."""
    t1 = time.time()
    unregister_module(module)

    module_init_path = os.path.join(ADDON_FOLDER, module, "__init__.py")
    if not os.path.exists(module_init_path):
        log_if(
            bpy.context.scene.sna.dev.log_reload_times,
            "WARNING",
            f"Cannot reload addon '{module}': __init__.py not found",
        )
        return

    addon_utils.enable(module, default_set=False, persistent=False)
    log_if(
        bpy.context.scene.sna.dev.log_reload_times,
        "INFO",
        f"Addon reloaded in {round(time.time() - t1, 4)}s",
    )


def unregister_module(module: str):
    """Unregister a module and remove from sys.modules."""
    # addon_utils.check returns (is_default, is_loaded)
    is_default, is_loaded = addon_utils.check(module)

    if is_loaded:
        addon_utils.disable(module, default_set=False)

    for name in list(sys.modules.keys()):
        if name.startswith(module):
            del sys.modules[name]


def get_module(module: str):
    addon_utils.modules_refresh()
    for mod in addon_utils.modules():
        if mod.__name__ == module:
            return mod
    return None
