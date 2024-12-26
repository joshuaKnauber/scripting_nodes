from scripting_nodes.src.lib.utils.logger import log_if
import addon_utils
import sys
import bpy
import time


def reload_addon(module: str):
    t1 = time.time()
    _unregister_modules(module)
    addon_utils.enable(module, default_set=True, persistent=True)
    log_if(
        bpy.context.scene.sna.dev.log_reload_times,
        "INFO",
        f"Addon reloaded in {round(time.time() - t1, 4)}s",
    )


def _unregister_modules(module: str):
    if not _has_module(module):
        return
    if addon_utils.check(module)[0]:
        addon_utils.disable(module)
    for name in list(sys.modules.keys()):
        if name.startswith(module):
            del sys.modules[name]


def _has_module(module: str):
    for mod in addon_utils.modules():
        if mod.__name__ == module:
            return True
    return False
