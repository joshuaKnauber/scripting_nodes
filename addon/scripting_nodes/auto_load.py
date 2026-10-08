import bpy
import sys
import typing
import inspect
import pkgutil
import importlib
import traceback
from pathlib import Path

__all__ = (
    "init",
    "register",
    "unregister",
)

blender_version = bpy.app.version

modules = None
ordered_classes = None


def init():
    global modules
    global ordered_classes

    modules = get_all_submodules(Path(__file__).parent)
    ordered_classes = get_ordered_classes_to_register(modules)


def register():
    registered = []
    try:
        for cls in ordered_classes:
            bpy.utils.register_class(cls)
            registered.append(cls)
    except Exception:
        # leave nothing half-registered behind
        for cls in reversed(registered):
            bpy.utils.unregister_class(cls)
        raise

    for module in modules:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "register"):
            module.register()


def unregister():
    # exact reverse of register: module hooks first, then classes
    for module in reversed(modules):
        if module.__name__ == __name__:
            continue
        if hasattr(module, "unregister"):
            try:
                module.unregister()
            except Exception:
                traceback.print_exc()

    for cls in reversed(ordered_classes):
        if getattr(cls, "is_registered", False):
            try:
                bpy.utils.unregister_class(cls)
            except Exception:
                traceback.print_exc()


def purge_modules():
    """Drop our submodules from sys.modules so the next init() re-imports them."""
    global modules, ordered_classes
    prefix = _package_name + "."
    for name in list(sys.modules):
        if name.startswith(prefix) and name != __name__:
            del sys.modules[name]
    modules = None
    ordered_classes = None


# Import modules
#################################################

# Store the package name at module load time
_package_name = __package__


def get_all_submodules(directory):
    return list(iter_submodules(directory, _package_name))


def iter_submodules(path, package_name):
    for name in sorted(iter_submodule_names(path)):
        yield importlib.import_module("." + name, package_name)


def iter_submodule_names(path, root=""):
    for _, module_name, is_package in pkgutil.iter_modules([str(path)]):
        if is_package:
            sub_path = path / module_name
            sub_root = root + module_name + "."
            yield from iter_submodule_names(sub_path, sub_root)
        else:
            yield root + module_name


# Find classes to register
#################################################


def get_ordered_classes_to_register(modules):
    return toposort(get_register_deps_dict(modules))


def get_register_deps_dict(modules):
    my_classes = set(iter_my_classes(modules))
    my_classes_by_idname = {
        cls.bl_idname: cls for cls in my_classes if hasattr(cls, "bl_idname")
    }

    deps_dict = {}
    for cls in my_classes:
        deps_dict[cls] = set(
            iter_my_register_deps(cls, my_classes, my_classes_by_idname)
        )
    return deps_dict


def iter_my_register_deps(cls, my_classes, my_classes_by_idname):
    yield from iter_my_deps_from_annotations(cls, my_classes)
    yield from iter_my_deps_from_parent_id(cls, my_classes_by_idname)


def iter_my_deps_from_annotations(cls, my_classes):
    for value in typing.get_type_hints(cls, {}, {}).values():
        dependency = get_dependency_from_annotation(value)
        if dependency is not None:
            if dependency in my_classes:
                yield dependency


def get_dependency_from_annotation(value):
    if blender_version >= (2, 93):
        if isinstance(value, bpy.props._PropertyDeferred):
            return value.keywords.get("type")
    else:
        if isinstance(value, tuple) and len(value) == 2:
            if value[0] in (bpy.props.PointerProperty, bpy.props.CollectionProperty):
                return value[1]["type"]
    return None


def iter_my_deps_from_parent_id(cls, my_classes_by_idname):
    if bpy.types.Panel in cls.__bases__:
        parent_idname = getattr(cls, "bl_parent_id", None)
        if parent_idname is not None:
            parent_cls = my_classes_by_idname.get(parent_idname)
            if parent_cls is not None:
                yield parent_cls


def iter_my_classes(modules):
    base_types = get_register_base_types()
    for cls in get_classes_in_modules(modules):
        # issubclass (not __bases__) so that classes inheriting through
        # intermediates like NodeCustomGroup are still picked up.
        if any(issubclass(cls, base) for base in base_types):
            if not getattr(cls, "is_registered", False):
                yield cls


def get_classes_in_modules(modules):
    classes = set()
    for module in modules:
        for cls in iter_classes_in_module(module):
            classes.add(cls)
    return classes


def iter_classes_in_module(module):
    for value in module.__dict__.values():
        if inspect.isclass(value):
            yield value


def get_register_base_types():
    return set(
        getattr(bpy.types, name)
        for name in [
            "Panel",
            "Operator",
            "PropertyGroup",
            "AddonPreferences",
            "Header",
            "Menu",
            "Node",
            "NodeSocket",
            "NodeTreeInterfaceSocket",
            "NodeTree",
            "UIList",
            "RenderEngine",
            "Gizmo",
            "GizmoGroup",
        ]
    )


# Find order to register to solve dependencies
#################################################


_BASE_PRIORITY = (
    "PropertyGroup",
    "NodeTree",
    "NodeSocket",
    "NodeTreeInterfaceSocket",
    "Node",
)


def _sort_key(cls):
    """Deterministic order: data types and trees/sockets before nodes."""
    for i, name in enumerate(_BASE_PRIORITY):
        if issubclass(cls, getattr(bpy.types, name)):
            return (i, cls.__module__, cls.__name__)
    return (len(_BASE_PRIORITY), cls.__module__, cls.__name__)


def toposort(deps_dict):
    sorted_list = []
    sorted_values = set()
    while len(deps_dict) > 0:
        unsorted = []
        ready = []
        for value, deps in deps_dict.items():
            if len(deps) == 0:
                ready.append(value)
            else:
                unsorted.append(value)
        if not ready:
            raise RuntimeError(f"Cyclic register dependencies: {list(deps_dict)}")
        ready.sort(key=_sort_key)
        sorted_list.extend(ready)
        sorted_values.update(ready)
        deps_dict = {value: deps_dict[value] - sorted_values for value in unsorted}
    return sorted_list
