from .....lib.utils.logger import log, log_if
from .....lib.constants.paths import ADDON_FOLDER
import addon_utils
import importlib
import sys
import bpy
import time
import os
import types


_REGISTERABLE_BASES = tuple(
    getattr(bpy.types, name)
    for name in (
        "Panel",
        "Operator",
        "PropertyGroup",
        "Menu",
        "Header",
        "UIList",
        "Node",
        "NodeSocket",
        "NodeTree",
        "AddonPreferences",
        "RenderEngine",
        "Gizmo",
        "GizmoGroup",
    )
    if hasattr(bpy.types, name)
)


def _classes_in_module(mod):
    """Yield bpy registerable classes DEFINED IN `mod` (not imported)."""
    mod_name = getattr(mod, "__name__", None)
    for value in vars(mod).values():
        if (
            isinstance(value, type)
            and issubclass(value, _REGISTERABLE_BASES)
            and getattr(value, "__module__", None) == mod_name
        ):
            yield value


def reload_tree_module(addon_module_name: str, tree_module_name: str):
    """Reload a single generated tree module without touching the rest of the addon.

    Steps:
      1. Find classes registered from the old module, unregister them
      2. Run the old module's unregister() (clears property/handler side effects)
      3. Snapshot public attrs (for rebinding step 6)
      4. Drop pyc + sys.modules entry, invalidate caches
      5. Re-import the module
      6. Register new classes, run new module's register()
      7. Rebind sibling tree modules that imported from this one
      8. Refresh the addon's auto_load.ordered_classes so future disable is clean
    """
    full_name = f"{addon_module_name}.addon.{tree_module_name}"
    old_mod = sys.modules.get(full_name)
    if old_mod is None:
        # Not loaded yet - just import fresh and register
        try:
            new_mod = importlib.import_module(full_name)
        except Exception as e:
            log("ERROR", f"reload_tree_module: initial import failed for {full_name}: {e}")
            return
        for cls in _classes_in_module(new_mod):
            try:
                bpy.utils.register_class(cls)
            except Exception:
                pass
        if hasattr(new_mod, "register"):
            try:
                new_mod.register()
            except Exception as e:
                log("WARNING", f"reload_tree_module: register failed for {full_name}: {e}")
        return

    # 1. unregister old classes
    old_classes = list(_classes_in_module(old_mod))
    for cls in reversed(old_classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass

    # 2. unregister side effects
    if hasattr(old_mod, "unregister"):
        try:
            old_mod.unregister()
        except Exception as e:
            log("WARNING", f"reload_tree_module: unregister failed for {full_name}: {e}")

    # 3. snapshot for rebinding (exclude modules and dunders)
    old_attrs = {
        k: v
        for k, v in vars(old_mod).items()
        if not k.startswith("_") and not isinstance(v, types.ModuleType)
    }

    # 4. drop pyc + sys.modules + invalidate caches
    addon_dir = os.path.join(ADDON_FOLDER, addon_module_name, "addon")
    pycache_dir = os.path.join(addon_dir, "__pycache__")
    if os.path.isdir(pycache_dir):
        prefix = f"{tree_module_name}.cpython"
        for f in os.listdir(pycache_dir):
            if f.startswith(prefix):
                try:
                    os.remove(os.path.join(pycache_dir, f))
                except OSError:
                    pass
    importlib.invalidate_caches()
    del sys.modules[full_name]

    # 5. re-import
    try:
        new_mod = importlib.import_module(full_name)
    except Exception as e:
        log("ERROR", f"reload_tree_module: re-import failed for {full_name}: {e}")
        return

    # 6. register new classes + run register()
    for cls in _classes_in_module(new_mod):
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            log("WARNING", f"reload_tree_module: register_class failed for {cls.__name__}: {e}")
    if hasattr(new_mod, "register"):
        try:
            new_mod.register()
        except Exception as e:
            log("WARNING", f"reload_tree_module: register() failed for {full_name}: {e}")

    # 7. rebind dependent sibling modules
    addon_pkg_prefix = f"{addon_module_name}.addon."
    for dep_name, dep_mod in list(sys.modules.items()):
        if dep_mod is None or dep_mod is new_mod:
            continue
        if not dep_name.startswith(addon_pkg_prefix):
            continue
        for attr_name in list(vars(dep_mod).keys()):
            current = getattr(dep_mod, attr_name, None)
            # `from . import tree_X` -> rebind module reference
            if current is old_mod:
                setattr(dep_mod, attr_name, new_mod)
                continue
            # `from .tree_X import name` -> rebind to new module's same-named attr
            if attr_name in old_attrs and current is old_attrs[attr_name]:
                new_val = getattr(new_mod, attr_name, None)
                if new_val is not None:
                    setattr(dep_mod, attr_name, new_val)

    # 8. refresh auto_load's class list so addon disable later is correct
    addon_root = sys.modules.get(addon_module_name)
    auto_load_mod = getattr(addon_root, "auto_load", None) if addon_root else None
    if auto_load_mod is not None and hasattr(auto_load_mod, "init"):
        try:
            auto_load_mod.init()
        except Exception as e:
            log("WARNING", f"reload_tree_module: auto_load.init() failed: {e}")


def reload_addon(module: str):
    """Reload an addon module (full disable + enable). Timing is reported by
    the watcher; this function stays silent on success and only warns when
    the addon files aren't on disk to enable."""
    unregister_module(module)
    module_init_path = os.path.join(ADDON_FOLDER, module, "__init__.py")
    if not os.path.exists(module_init_path):
        log(
            "WARNING",
            f"Cannot reload addon '{module}': __init__.py not found",
        )
        return
    addon_utils.enable(module, default_set=False, persistent=False)


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
