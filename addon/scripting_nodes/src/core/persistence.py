"""Small JSON store remembering which generated addon belongs to which file.

    {"files": {"<addon uid>": {"module": "my_addon", "persist": false}}}

Lives in the extension's user directory, so updating or reinstalling
Scripting Nodes doesn't wipe it (the install folder is replaced on update).
Used to
  - remove the previous folder when an addon is renamed (even across sessions)
  - re-enable addons marked "persist" after loading another .blend file
"""

import json
import os

import bpy

_ROOT_PACKAGE = __package__.rsplit(".src.", 1)[0]


def _store_path():
    try:
        folder = bpy.utils.extension_path_user(_ROOT_PACKAGE, create=True)
    except (ValueError, RuntimeError):
        # not installed as an extension (legacy add-on install)
        folder = bpy.utils.user_resource("CONFIG", path="scripting_nodes", create=True)
    return os.path.join(folder, "generated_addons.json")


def _load():
    try:
        with open(_store_path()) as f:
            data = json.load(f)
        if isinstance(data.get("files"), dict):
            return data
    except (OSError, ValueError):
        pass
    return {"files": {}}


def _save(data):
    with open(_store_path(), "w") as f:
        json.dump(data, f, indent=2)


def module_for(uid: str) -> str | None:
    return _load()["files"].get(uid, {}).get("module")


def track(uid: str, module: str, persist: bool):
    data = _load()
    entry = {"module": module, "persist": persist}
    if data["files"].get(uid) != entry:
        data["files"][uid] = entry
        _save(data)


def persisted_modules() -> list[str]:
    return [info["module"] for info in _load()["files"].values() if info.get("persist")]
