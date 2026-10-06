from ...core.generator import generate_addon
from ...core.modules.modules import (
    unregister_module,
)
from ...core.modules.persisted import (
    track_module,
)
import addon_utils
import bpy
from bpy.app.handlers import persistent


@persistent
def on_save_pre(dummy):
    addon = bpy.context.scene.sna.addon
    uid = addon.get_uid()
    module_name = addon.module_name
    persist = addon.persist_addon

    # Track module by UID (handles rename detection) and set persist status
    track_module(uid, module_name, persist=persist)

    if persist:
        # Unregister the current addon first
        unregister_module(module_name)
        # Regenerate and re-enable so the saved .blend points at fresh files
        generate_addon()
        addon_utils.enable(module_name, default_set=False, persistent=False)


def register():
    bpy.app.handlers.save_pre.append(on_save_pre)


def unregister():
    bpy.app.handlers.save_pre.remove(on_save_pre)
