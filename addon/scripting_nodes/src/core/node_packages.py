"""Node packages: zips of extra nodes, installed into the extension's user
folder (`node_packages/<id>/`) and loaded as subpackages of `src.node_packages`
(its `__path__` gets that folder; `sys` stays untouched). auto_load imports
and registers them after Scripting Nodes itself, each one on its own: a
broken package shows its error in the Preferences and the rest still loads.

    text_tools.zip
        nodes.toml             optional: id, name, version, author, api
        interface/node_x.py    a category folder: merged with the built-in one
        text_tools/node_y.py   any other name is a new category

Index files (`__init__.py`) are written where they're missing; they pass the
node API (src/api.py) down, so node files `from . import sn` at any depth.
"""

import os
import re
import shutil
import tempfile
import tomllib
import traceback
import zipfile
from dataclasses import dataclass, field

import bpy

ROOT_PACKAGE = __package__.rsplit(".src.", 1)[0]
CONTAINER = __package__.rsplit(".", 1)[0] + ".node_packages"
META = "nodes.toml"


class InstallError(Exception):
    pass


@dataclass
class Package:
    id: str
    path: str
    name: str = ""
    version: str = ""
    author: str = ""
    api: int = 1
    modules: list = field(default_factory=list)
    classes: list = field(default_factory=list)
    error: str = ""

    @property
    def module_name(self):
        return f"{CONTAINER}.{self.id}"

    @property
    def nodes(self):
        return [cls for cls in self.classes if issubclass(cls, bpy.types.Node)]


# id -> Package, of the last load (auto_load)
packages: dict[str, Package] = {}


def install_folder() -> str:
    """Where packages are installed (kept when Scripting Nodes is updated)."""
    try:
        base = bpy.utils.extension_path_user(ROOT_PACKAGE, create=True)
    except (ValueError, RuntimeError):
        # not installed as an extension (legacy add-on install)
        base = bpy.utils.user_resource("CONFIG", path="scripting_nodes", create=True)
    folder = os.path.join(base, "node_packages")
    os.makedirs(folder, exist_ok=True)
    return folder


def package_id(text: str) -> str:
    """A Python identifier from a name: `Text Tools-1.2.zip` -> `text_tools_1_2`."""
    text = re.sub(r"\.zip$", "", text, flags=re.I)
    name = re.sub(r"[^0-9a-zA-Z]+", "_", text).strip("_").lower()
    if not name:
        return "package"
    return f"package_{name}" if name[0].isdigit() else name


def _api_version():
    from ..api import API_VERSION

    return API_VERSION


# -- reading ------------------------------------------------------------------


def read_meta(text: str | None, fallback_id: str) -> dict:
    """The meta file's settings (all optional) with defaults."""
    meta = {}
    if text is not None:
        try:
            meta = tomllib.loads(text)
        except tomllib.TOMLDecodeError as exc:
            raise InstallError(f"{META} isn't valid TOML: {exc}") from None
    pid = package_id(str(meta.get("id") or fallback_id))
    api = meta.get("api", 1)
    if not isinstance(api, int):
        raise InstallError(f"{META}: api must be a number")
    return {
        "id": pid,
        "name": str(meta.get("name") or pid.replace("_", " ").title()),
        "version": str(meta.get("version", "")),
        "author": str(meta.get("author", "")),
        "api": api,
    }


def discover() -> list[Package]:
    """The installed packages, by id."""
    found = []
    root = install_folder()
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if not os.path.isfile(os.path.join(path, "__init__.py")):
            continue
        meta_path = os.path.join(path, META)
        try:
            text = None
            if os.path.isfile(meta_path):
                with open(meta_path, encoding="utf-8") as f:
                    text = f.read()
            meta = read_meta(text, name)
            meta["id"] = name  # the folder is what's imported
            found.append(Package(path=path, **meta))
        except InstallError as exc:
            found.append(Package(id=name, path=path, name=name, error=str(exc)))
    return found


# -- loading (auto_load) ------------------------------------------------------


def _module_names(package):
    """Dotted names of the package's modules, packages first."""
    names = [package.module_name]
    for folder, dirs, files in os.walk(package.path):
        dirs[:] = sorted(d for d in dirs if not d.startswith((".", "__")))
        rel = os.path.relpath(folder, package.path)
        prefix = package.module_name + (
            "" if rel == "." else "." + rel.replace(os.sep, ".")
        )
        if rel != "." and not os.path.isfile(os.path.join(folder, "__init__.py")):
            dirs[:] = []
            continue
        if rel != ".":
            names.append(prefix)
        for file in sorted(files):
            if file.endswith(".py") and file != "__init__.py":
                names.append(f"{prefix}.{file[:-3]}")
    return names


def load_all() -> list[Package]:
    """Import every installed package (errors stay with their package)."""
    import importlib

    packages.clear()
    for package in discover():
        packages[package.id] = package
        if package.error:
            continue
        if package.api > _api_version():
            package.error = (
                f"Needs a newer Scripting Nodes (node API {package.api}, "
                f"this one has {_api_version()})"
            )
            continue
        try:
            package.modules = [
                importlib.import_module(n) for n in _module_names(package)
            ]
        except Exception as exc:  # noqa: BLE001 - the package's own code
            package.modules = []
            package.error = _short_error(exc)
            traceback.print_exc()
    return list(packages.values())


def _short_error(exc):
    tb = traceback.extract_tb(exc.__traceback__)
    where = next((f for f in reversed(tb) if "node_packages" in f.filename), None)
    place = (
        f" ({os.path.basename(where.filename)}, line {where.lineno})" if where else ""
    )
    return f"{type(exc).__name__}: {exc}{place}"


def category_path(module_name: str) -> list[str] | None:
    """Add menu category of a package module: its folders, the package's id
    for files at its top. None for modules of Scripting Nodes itself."""
    prefix = CONTAINER + "."
    if not module_name.startswith(prefix):
        return None
    parts = module_name[len(prefix) :].split(".")
    folders = parts[1:-1]
    return folders or [parts[0]]


# -- installing ---------------------------------------------------------------


def _members(archive):
    """The archive's files (relative paths), without a single folder all of
    them are in (zips of a folder)."""
    names = [n for n in archive.namelist() if not n.endswith("/")]
    for name in names:
        parts = name.split("/")
        if name.startswith("/") or ".." in parts or ":" in parts[0]:
            raise InstallError(f"Unsafe path in the zip: {name}")
    names = [n for n in names if "__MACOSX" not in n and "__pycache__" not in n]
    tops = {n.split("/", 1)[0] for n in names}
    strip = ""
    if len(tops) == 1 and all("/" in n for n in names):
        strip = next(iter(tops)) + "/"
    return [(n, n[len(strip) :]) for n in names]


def install(zip_path: str) -> Package:
    """Install (or replace) the package in `zip_path`. Loads with the next
    reload of Scripting Nodes (reload())."""
    if not zipfile.is_zipfile(zip_path):
        raise InstallError("Not a zip file")
    with zipfile.ZipFile(zip_path) as archive:
        members = _members(archive)
        if not any(rel.endswith(".py") for _, rel in members):
            raise InstallError("The zip has no Python files")
        meta_member = next((n for n, rel in members if rel == META), None)
        text = archive.read(meta_member).decode("utf-8") if meta_member else None
        meta = read_meta(text, os.path.basename(zip_path))
        if meta["api"] > _api_version():
            raise InstallError(
                f"Needs a newer Scripting Nodes (node API {meta['api']}, "
                f"this one has {_api_version()})"
            )
        with tempfile.TemporaryDirectory() as temp:
            staged = os.path.join(temp, meta["id"])
            for name, rel in members:
                target = os.path.join(staged, *rel.split("/"))
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with archive.open(name) as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)
            write_index_files(staged, meta["name"])
            destination = os.path.join(install_folder(), meta["id"])
            if os.path.exists(destination):
                shutil.rmtree(destination)
            shutil.move(staged, destination)
    return Package(path=destination, **meta)


ROOT_INDEX = '''"""{name}: a node package (index file written by Scripting Nodes)."""

from ... import api as sn  # noqa: F401 - node files: `from . import sn`
'''
FOLDER_INDEX = '''"""Index file written by Scripting Nodes."""

from .. import sn  # noqa: F401 - node files: `from . import sn`
'''


def write_index_files(root: str, name: str):
    """An `__init__.py` in every folder that has none; ones the package has
    get the line passing `sn` down if they don't have it."""
    for folder, dirs, _files in os.walk(root):
        dirs[:] = [d for d in dirs if not d.startswith((".", "__"))]
        is_root = os.path.samefile(folder, root)
        path = os.path.join(folder, "__init__.py")
        content = ROOT_INDEX.format(name=name) if is_root else FOLDER_INDEX
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            continue
        with open(path, encoding="utf-8") as f:
            own = f.read()
        if not re.search(r"\bimport\b.*\bsn\b", own):
            line = content.strip().splitlines()[-1]
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"{line}\n{own}")


def remove(pid: str):
    """Delete an installed package (its nodes go with the next reload)."""
    path = os.path.join(install_folder(), pid)
    if not os.path.isdir(path):
        raise InstallError(f"No package '{pid}'")
    shutil.rmtree(path)


def reload():
    """Disable and enable Scripting Nodes on a timer (not from inside one of
    its operators), so packages are loaded or dropped."""
    import addon_utils

    def run():
        addon_utils.disable(ROOT_PACKAGE, default_set=False)
        addon_utils.enable(ROOT_PACKAGE, default_set=False)

    bpy.app.timers.register(run, first_interval=0.01)
