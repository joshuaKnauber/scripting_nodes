import os

from scripting_nodes.src.lib.constants.paths import DEV_ADDON_MODULE


LAST_MODULES_TO_REMOVE = None


def add_module_to_remove(module_name):
    global LAST_MODULES_TO_REMOVE
    if module_name == DEV_ADDON_MODULE:
        return
    modules = get_modules_to_remove()
    modules = list(set(modules + [module_name]))
    with open(_remove_path(), "w+") as f:
        f.writelines([f"{module}\n" for module in modules])
    LAST_MODULES_TO_REMOVE = modules


def get_modules_to_remove():
    global LAST_MODULES_TO_REMOVE
    if LAST_MODULES_TO_REMOVE is not None:
        return LAST_MODULES_TO_REMOVE
    modules = []
    if not os.path.exists(_remove_path()):
        return modules
    with open(_remove_path(), "r") as f:
        for line in f.readlines():
            if line.strip():
                modules.append(line.strip())
    LAST_MODULES_TO_REMOVE = modules
    return modules


def clear_modules_to_remove():
    global LAST_MODULES_TO_REMOVE
    if not os.path.exists(_remove_path()):
        return
    with open(_remove_path(), "w") as f:
        f.truncate()
    LAST_MODULES_TO_REMOVE = []


def _remove_path():
    return os.path.join(os.path.dirname(__file__), "to_remove.txt")
