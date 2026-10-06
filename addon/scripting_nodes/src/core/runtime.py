"""Owns the generated addon on disk and in Blender.

`apply(files)` makes the folder `<user scripts>/addons/<module_name>` match
`files` and (re)loads the addon - transactionally:

  1. changed modules are syntax-checked before anything is touched; on error
     the previous version keeps running and the error is shown
  2. files are written, then the addon is fully disabled and enabled again
  3. if the new version fails to import or register, the previous files are
     restored and the previous version is loaded again

Only folders created by Scripting Nodes are ever written to or deleted (they
contain a marker file), so a user's own addon with the same name is safe.
"""

import importlib
import os
import shutil
import sys

import addon_utils
import bpy

from ..lib.logger import log
from ..lib.paths import ADDON_FOLDER
from . import errors, persistence

MARKER = ".scripting_nodes"
_LEGACY_SIGNATURE = "Add-on created with Scripting Nodes"

# Module name of the addon this session loaded (None if nothing loaded)
_loaded: str | None = None


def folder(module: str) -> str:
    return os.path.join(ADDON_FOLDER, module)


def is_owned(path: str) -> bool:
    """True if `path` was created by Scripting Nodes (safe to overwrite/delete)."""
    if os.path.exists(os.path.join(path, MARKER)):
        return True
    # folders generated before the marker existed
    init = os.path.join(path, "__init__.py")
    if os.path.isdir(os.path.join(path, "addon")) and os.path.exists(init):
        with open(init, errors="ignore") as f:
            return _LEGACY_SIGNATURE in f.read()
    return False


def is_loaded(module: str) -> bool:
    mod = sys.modules.get(module) if module else None
    return bool(getattr(mod, "__addon_enabled__", False))


def loaded_module() -> str | None:
    return _loaded


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------


def apply(files: dict[str, str]) -> bool:
    """Sync disk + Blender with `files`. Returns True if the addon was reloaded."""
    global _loaded
    settings = bpy.context.scene.sna.addon
    module = settings.module_name
    uid = settings.get_uid()

    # Renamed (now or in an earlier session): drop the old addon
    previous = {_loaded, persistence.module_for(uid)} - {None, module}
    for old in previous:
        unload(old)
        remove_folder(old)
    if _loaded != module:
        _loaded = None

    if not files or not settings.enabled:
        unload(module)
        _loaded = None
        if not files:
            remove_folder(module)
        errors.set_addon_error(None)
        return False

    path = folder(module)
    if os.path.exists(path) and not is_owned(path):
        errors.set_addon_error(
            f"'{path}' already exists and wasn't created by Scripting Nodes. "
            "Rename the addon or remove that folder."
        )
        return False

    current = _read_folder(path)
    changed = {rel: src for rel, src in files.items() if current.get(rel) != src}
    stale = [rel for rel in current if rel.startswith("addon/") and rel not in files]
    was_loaded = is_loaded(module)
    if not changed and not stale and was_loaded:
        _loaded = module
        return False

    syntax_error = _check_syntax(changed)
    if syntax_error:
        errors.set_addon_error(syntax_error)
        log("ERROR", syntax_error)
        return False

    _write_folder(path, changed, stale)
    persistence.track(uid, module, settings.persist_addon)
    ok, error = reload(module)
    if ok:
        _loaded = module
        errors.set_addon_error(None)
        return True

    log("ERROR", f"Generated addon failed to load, keeping previous version:\n{error}")
    errors.set_addon_error(error)
    if was_loaded and current:
        # Back to what was running before
        _write_folder(path, current, [rel for rel in files if rel not in current])
        restored, _ = reload(module)
        _loaded = module if restored else None
    else:
        _loaded = None
    return True


def _check_syntax(files):
    for rel, source in files.items():
        if not rel.endswith(".py"):
            continue
        try:
            compile(source, rel, "exec")
        except SyntaxError as e:
            return (
                f"Generated code has a syntax error in {rel}, line {e.lineno}: {e.msg}"
            )
    return None


def _read_folder(path):
    files = {}
    if not os.path.isdir(path):
        return files
    for root, dirs, names in os.walk(path):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in names:
            if name == MARKER:
                continue
            full = os.path.join(root, name)
            rel = os.path.relpath(full, path).replace(os.sep, "/")
            try:
                with open(full, encoding="utf-8") as f:
                    files[rel] = f.read()
            except (OSError, UnicodeDecodeError):
                pass
    return files


def _write_folder(path, files, remove):
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, MARKER), "w") as f:
        f.write("This folder is generated by Scripting Nodes. Edits are overwritten.\n")
    for rel, source in files.items():
        full = os.path.join(path, *rel.split("/"))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(source)
    for rel in remove:
        full = os.path.join(path, *rel.split("/"))
        if os.path.isfile(full):
            os.remove(full)
    # .pyc files are validated by mtime in whole seconds + size; a quick edit
    # of the same length (e.g. changing one digit) would load stale bytecode.
    for root, dirs, _names in os.walk(path):
        if "__pycache__" in dirs:
            shutil.rmtree(os.path.join(root, "__pycache__"), ignore_errors=True)
            dirs.remove("__pycache__")


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def reload(module: str) -> tuple[bool, str | None]:
    """Fully disable + enable `module`. Returns (ok, error text)."""
    unload(module)
    # Blender only adds scripts/addons to sys.path if it existed at startup
    if ADDON_FOLDER not in sys.path:
        sys.path.append(ADDON_FOLDER)
    importlib.invalidate_caches()
    failures = []
    mod = addon_utils.enable(
        module,
        default_set=False,
        persistent=False,
        handle_error=lambda exc: failures.append(errors.format_exception(exc)),
    )
    if mod is None or failures:
        unload(module)
        return False, "\n".join(failures) or f"Could not enable '{module}'"
    return True, None


def unload(module: str | None):
    """Disable `module` and forget all its Python modules."""
    if not module:
        return
    if is_loaded(module):
        addon_utils.disable(
            module,
            default_set=False,
            handle_error=lambda exc: log(
                "WARNING", f"Error while disabling {module}: {exc}"
            ),
        )
    for name in list(sys.modules):
        if name == module or name.startswith(module + "."):
            del sys.modules[name]


def remove_folder(module: str):
    path = folder(module)
    if module and os.path.isdir(path) and is_owned(path):
        shutil.rmtree(path, ignore_errors=True)


def unload_current():
    """Called before loading another file (unless the addon persists)."""
    global _loaded
    unload(_loaded)
    _loaded = None


def enable_persisted():
    """Enable addons the user marked as "persist" (after loading a file)."""
    for module in persistence.persisted_modules():
        if os.path.exists(os.path.join(folder(module), "__init__.py")):
            if not is_loaded(module):
                ok, error = reload(module)
                if not ok:
                    log(
                        "WARNING", f"Persisted addon '{module}' failed to load: {error}"
                    )
