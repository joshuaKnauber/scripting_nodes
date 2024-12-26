from scripting_nodes.src.lib.constants.paths import DEV_ADDON_MODULE
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


def unregister_last_module():
    if bpy.context.scene.sna.addon.force_production:
        unregister_module(bpy.context.scene.sna.addon.module_name)
    else:
        unregister_module(DEV_ADDON_MODULE)


def unregister_module(module: str):
    print(module)
    if not _has_module(module):
        print("no module")
        return
    print("yes module")
    if addon_utils.check(module)[0]:
        print("disable")
        addon_utils.disable(module, default_set=True)
    for name in list(sys.modules.keys()):
        if name.startswith(module):
            print("delete")
            del sys.modules[name]


def _has_module(module: str):
    for mod in addon_utils.modules():
        if mod.__name__ == module:
            return True
    return False
