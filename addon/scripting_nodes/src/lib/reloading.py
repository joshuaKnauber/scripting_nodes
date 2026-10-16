"""Reload a package's modules with the code on disk, the ones others import
from first, without changing `sys.modules` (extensions mustn't touch `sys`).
Modules of removed files stay unused."""

import ast
import importlib
import os
import sys


def reload_package(package: str, skip=()):
    """Reload the loaded modules of `package` (and it, unless skipped)."""
    loaded = {
        name: module
        for name, module in list(sys.modules.items())
        if module is not None
        and (name == package or name.startswith(package + "."))
        and name not in skip
        and getattr(module, "__file__", None)
        and os.path.exists(module.__file__)
    }
    for name in import_order(loaded):
        importlib.reload(loaded[name])


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
