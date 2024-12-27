from scripting_nodes.src.lib.utils.logger import log_if
import addon_utils
import sys
import bpy
import time


def reload_addon(module: str):
    t1 = time.time()
    unregister_module(module)
    addon_utils.enable(module, default_set=True, persistent=True)
    log_if(
        bpy.context.scene.sna.dev.log_reload_times,
        "INFO",
        f"Addon reloaded in {round(time.time() - t1, 4)}s",
    )


def unregister_module(module: str):
    if addon_utils.check(module)[0]:
        addon_utils.disable(module, default_set=True)

    for name in list(sys.modules.keys()):
        if name.startswith(module):
            del sys.modules[name]


def get_module(module: str):
    addon_utils.modules_refresh()
    for mod in addon_utils.modules():
        if mod.__name__ == module:
            return mod
    return None
