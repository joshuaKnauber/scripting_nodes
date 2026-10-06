import os
import json


def _persist_path():
    return os.path.join(os.path.dirname(__file__), "persisted.json")


def _load_data():
    """Load the persistence data from JSON.

    Structure:
    {
        "files": {
            "UID": {
                "module": "module_name",
                "persist": true/false
            },
            ...
        },
        "pending_removal": ["module_name", ...]
    }
    """
    if not os.path.exists(_persist_path()):
        return {"files": {}, "pending_removal": []}
    try:
        with open(_persist_path(), "r") as f:
            data = json.load(f)
            if "files" not in data or not isinstance(data["files"], dict):
                data["files"] = {}
            if "pending_removal" not in data:
                data["pending_removal"] = []
            return data
    except (json.JSONDecodeError, IOError):
        return {"files": {}, "pending_removal": []}


def _save_data(data):
    """Save the persistence data to JSON."""
    with open(_persist_path(), "w") as f:
        json.dump(data, f, indent=2)


def get_persisted_modules():
    """Get list of module names that should stay enabled across file loads."""
    data = _load_data()
    return [
        info["module"] for info in data["files"].values() if info.get("persist", False)
    ]


def get_pending_removal():
    """Get list of modules pending removal."""
    return _load_data()["pending_removal"]


def track_module(uid, module_name, persist=False):
    """Track a module by UID, detecting renames.

    If the UID exists with a different module_name, the old module
    is marked for pending removal.

    Args:
        uid: Unique identifier for the file
        module_name: Current module name
        persist: Whether to keep enabled across file loads
    """
    data = _load_data()

    # Check if UID exists with a different module name (rename case)
    if uid in data["files"]:
        old_module = data["files"][uid]["module"]
        if old_module != module_name:
            # Mark old module for removal
            if old_module not in data["pending_removal"]:
                data["pending_removal"].append(old_module)

    # Update the file entry
    data["files"][uid] = {"module": module_name, "persist": persist}

    # Remove new module from pending removal if present
    if module_name in data["pending_removal"]:
        data["pending_removal"].remove(module_name)

    _save_data(data)


def clear_pending_removal():
    """Clear the pending removal list (after cleanup is done)."""
    data = _load_data()
    data["pending_removal"] = []
    _save_data(data)


def is_persisted(uid):
    """Check if a UID is set to persist."""
    data = _load_data()
    return data["files"].get(uid, {}).get("persist", False)
