"""Reload a package's modules with the code on disk, the ones others import
from first, without changing `sys.modules` (extensions mustn't touch `sys`).
Modules of removed files stay unused, unless their name is back as another
kind of file (a module where there was a package, or the reverse)."""

import ast
import importlib
import os
import sys
import types


def reload_package(package: str, skip=()):
    """Reload the loaded modules of `package` (and it, unless skipped)."""
    root = sys.modules.get(package)
    root = os.path.dirname(root.__file__) if getattr(root, "__file__", None) else None
    loaded = {}
    for name, module in list(sys.modules.items()):
        if (
            module is None
            or not (name == package or name.startswith(package + "."))
            or name in skip
            or not getattr(module, "__file__", None)
        ):
            continue
        if os.path.exists(module.__file__):
            loaded[name] = module
            continue
        # its file is gone, but the name may be back as a module where there
        # was a package (or the other way around): reload finds it again
        found = _on_disk(root, name[len(package) + 1 :]) if root else None
        if found is not None:
            if not found.endswith("__init__.py") and hasattr(module, "__path__"):
                del module.__path__  # not a package anymore
            loaded[name] = module
    for module in loaded.values():
        if getattr(module, "__path__", None):
            _forget_submodules(module, package)
    for name in import_order(loaded):
        importlib.reload(loaded[name])


def _on_disk(root, relative):
    """File of module `relative` ("a.b") in folder `root`, None if missing."""
    base = os.path.join(root, *relative.split(".")) if relative else root
    for path in (base + ".py", os.path.join(base, "__init__.py")):
        if os.path.exists(path):
            return path
    return None


def _forget_submodules(module, package):
    """Remove the package's names for modules of `package`. `from . import x`
    takes `x` from the package before sys.modules: a reload runs the code
    again in the same namespace, so a name could still point at a module that
    moved (e.g. `x` from `.ui` when x.py is now at the top). They're bound
    again when the package is reloaded (or found in sys.modules)."""
    for key, value in list(vars(module).items()):
        if isinstance(value, types.ModuleType) and value.__name__.startswith(
            package + "."
        ):
            delattr(module, key)


def import_order(loaded: dict) -> list[str]:
    """Names of the `loaded` modules ({name: module}), the ones others import
    from first."""
    deps = {}
    for name, module in loaded.items():
        package = name if getattr(module, "__path__", None) else name.rpartition(".")[0]
        try:
            with open(module.__file__, encoding="utf-8") as f:
                tree = ast.parse(f.read())
        except (OSError, SyntaxError):
            tree = ast.Module(body=[], type_ignores=[])
        found = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level:
                base = (
                    package.rsplit(".", node.level - 1)[0]
                    if node.level > 1
                    else package
                )
                target = f"{base}.{node.module}" if node.module else base
                if node.module:  # `from . import x` imports x, not the package
                    found.add(target)
                found |= {f"{target}.{alias.name}" for alias in node.names}
        deps[name] = (found & set(loaded)) - {name}
    order, done = [], set()

    def visit(name, path=()):
        if name in done or name in path:
            return
        for dep in sorted(deps[name]):
            visit(dep, (*path, name))
        done.add(name)
        order.append(name)

    for name in sorted(loaded, key=lambda n: (n.count("."), n), reverse=True):
        visit(name)
    return order
