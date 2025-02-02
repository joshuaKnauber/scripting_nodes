import os


def add_module_to_persist(module_name):
    modules = get_modules_to_persist()
    modules = list(set(modules + [module_name]))
    with open(_persist_path(), "w+") as f:
        f.writelines([f"{module}\n" for module in modules])


def remove_module_to_persist(module_name):
    modules = get_modules_to_persist()
    modules = list(set(modules) - {module_name})
    with open(_persist_path(), "w+") as f:
        f.writelines([f"{module}\n" for module in modules])


def get_modules_to_persist():
    modules = []
    if not os.path.exists(_persist_path()):
        return []
    with open(_persist_path(), "r") as f:
        for line in f.readlines():
            if line.strip():
                modules.append(line.strip())
    return modules


def _persist_path():
    return os.path.join(os.path.dirname(__file__), "persisted.txt")
