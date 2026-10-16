"""Properties: finding them, picking them from nodes and their code.

Definitions live in lists (settings/properties.py). Add-on properties
compile to their own module, `properties.py`:

    class MY_ADDON_PG_scene_properties(bpy.types.PropertyGroup):
        count: bpy.props.IntProperty(name="Count", default=3)

    def register():
        bpy.types.Scene.my_addon = bpy.props.PointerProperty(type=MY_ADDON_PG_scene_properties)

Operator / Preferences properties are annotations in that node's class
(`annotations(node, ctx)`). Nodes reference a property by id and pick it in
a search field (`reference()`).
"""

from typing import NamedTuple

import bpy

from ..lib.code_format import sort_imports
from ..lib.icons import is_builtin
from . import errors, naming

PROPERTIES_MODULE = "properties"

# picker category -> property types offered
CATEGORIES = {
    "ALL": {"BOOLEAN", "INTEGER", "FLOAT", "VECTOR", "STRING", "ENUM", "POINTER", "COLLECTION"},
    "UPDATE": {"BOOLEAN", "INTEGER", "FLOAT", "VECTOR", "STRING", "ENUM", "POINTER"},
    "BOOLEAN": {"BOOLEAN"},
    "NUMBER": {"INTEGER", "FLOAT"},
    "INTEGER": {"INTEGER"},
    "STRING": {"STRING"},
    "VECTOR": {"VECTOR"},
    "ENUM": {"ENUM"},
    "POINTER": {"POINTER"},
    "COLLECTION": {"COLLECTION"},
    "GROUP": {"GROUP"},
}  # fmt: skip

# attach type -> where its data is in a context
CONTEXT_OWNERS = {
    "Scene": "scene",
    "Object": "object",
    "WindowManager": "window_manager",
    "Material": "material",
    "Collection": "collection",
    "Bone": "active_bone",
    "PoseBone": "active_pose_bone",
    "Node": "active_node",
    "Strip": "active_strip",
    "ViewLayer": "view_layer",
    "WorkSpace": "workspace",
}

PREFERENCES = "{context}.preferences.addons[__package__].preferences"


# -----------------------------------------------------------------------------
# Finding properties
# -----------------------------------------------------------------------------


class Found(NamedTuple):
    prop: object
    kind: str  # ADDON, GROUP or NODE
    owner: object  # None, the group or the node
    items: object  # the list it is in


def addon_settings():
    return bpy.context.scene.sna.addon


def lists():
    """(kind, owner, items) of every property list."""
    from ..lib.trees import scripting_node_trees, sn_nodes

    addon = addon_settings()
    result = [("ADDON", None, addon.properties)]
    for prop in addon.properties:
        if prop.property_type == "GROUP":
            result.append(("GROUP", prop, prop.members))
    for tree in sorted(scripting_node_trees(), key=lambda t: t.name):
        for node in sorted(sn_nodes(tree), key=lambda n: n.name):
            if hasattr(node, "properties"):
                result.append(("NODE", node, node.properties))
    return result


def find(prop_id) -> Found | None:
    if not prop_id:
        return None
    for kind, owner, items in lists():
        for prop in items:
            if prop.id == prop_id:
                return Found(prop, kind, owner, items)
    return None


def groups():
    return [p for p in addon_settings().properties if p.property_type == "GROUP"]


def find_group(group_id):
    return next((g for g in groups() if g.id == group_id), None)


# attributes properties can't use: methods / properties every PropertyGroup,
# Operator and AddonPreferences already has (items(), keys(), layout, ...)
RESERVED_ATTRIBUTES = {
    name
    for cls in (bpy.types.PropertyGroup, bpy.types.Operator, bpy.types.AddonPreferences)
    for name in dir(cls)
    if not name.startswith("_")
}


def python_names(items) -> dict:
    """{property id: name in code}, unique within one list."""
    used = set(RESERVED_ATTRIBUTES)
    result = {}
    for prop in items:
        base = naming.snake(prop.python_name or prop.name, "prop")
        if base.startswith("bl_"):
            base = "prop_" + base
        result[prop.id] = naming.unique(base, used)
    return result


def python_name(found: Found) -> str:
    return python_names(found.items)[found.prop.id]


def addon_attribute():
    """`scene.<this>.count`: the add-on's group on Blender data."""
    return addon_settings().module_name


def label(found: Found) -> str:
    if found.kind == "GROUP":
        return f"{found.owner.name} › {found.prop.name}"
    if found.kind == "NODE":
        return f"{naming.label(found.owner)} › {found.prop.name}"
    return found.prop.name


# -----------------------------------------------------------------------------
# References from nodes (picked by name, stored by id)
# -----------------------------------------------------------------------------


def choices(category):
    """(label, property) of every property of `category`, labels unique."""
    types = CATEGORIES[category]
    result, seen = [], set()
    for kind, owner, items in lists():
        for prop in items:
            if prop.property_type in types:
                text = naming.unique(label(Found(prop, kind, owner, items)), seen)
                result.append((text, prop))
    return result


def reference(attr, category, **kwargs):
    """A StringProperty showing the picked property's name, storing its id in
    `<attr>_id`. Its search field offers the properties of `category`.
    Setting it rebuilds the add-on."""
    key = attr + "_id"

    # the declared `<attr>_id` property, not self[key]: Blender keeps
    # declared properties apart from custom properties
    def get(self):
        found = find(getattr(self, key))
        return label(found) if found else ""

    def set(self, value):
        if value:
            prop = next((p for text, p in choices(category) if text == value), None)
            if prop is None:
                return  # text that isn't a choice keeps the current one
            setattr(self, key, prop.id)
        else:
            setattr(self, key, "")
        mark = getattr(self, "mark_dirty", None)
        if mark:
            mark()
        else:
            from . import scheduler

            scheduler.request_full()

    def search(self, context, edit_text):
        return [(text, p.property_type.title()) for text, p in choices(category)]

    return bpy.props.StringProperty(get=get, set=set, search=search, **kwargs)


def is_missing(owner, attr) -> bool:
    """True if field `attr` points at a property that doesn't exist (anymore)."""
    prop_id = getattr(owner, attr + "_id")
    return bool(prop_id) and find(prop_id) is None


def draw_reference(layout, owner, attr, text=""):
    """A property field: search field, red if its property was deleted."""
    row = layout.row(align=True)
    if is_missing(owner, attr):
        row.alert = True
        row.prop(owner, attr, text=text, icon="ERROR")
    else:
        row.prop(owner, attr, text=text)
    return row


def install_references(cls, refs):
    """`refs`: {attribute: picker category}, see ScriptingBaseNode."""
    annotations = cls.__dict__.get("__annotations__")
    if annotations is None:
        annotations = cls.__annotations__ = {}
    for attr, category in refs.items():
        annotations[attr] = reference(attr, category, name="Property")
        annotations[attr + "_id"] = bpy.props.StringProperty(options={"HIDDEN"})


# -----------------------------------------------------------------------------
# Values in code
# -----------------------------------------------------------------------------

SOCKETS = {
    "BOOLEAN": "ScriptingBooleanSocket",
    "INTEGER": "ScriptingIntegerSocket",
    "FLOAT": "ScriptingFloatSocket",
    "STRING": "ScriptingStringSocket",
    "ENUM": "ScriptingStringSocket",
    "POINTER": "ScriptingBlendDataSocket",
    "COLLECTION": "ScriptingBlendDataSocket",
}


def socket_type(prop) -> str:
    """Socket type of the property's values."""
    if prop.property_type == "VECTOR" and prop.vector_type == "BOOLEAN":
        return "ScriptingListSocket"
    if prop.property_type == "VECTOR":
        if prop.subtype_vector in {"COLOR", "COLOR_GAMMA"}:
            return "ScriptingColorSocket"
        return "ScriptingVectorSocket"
    if prop.property_type == "ENUM" and prop.enum_flag:
        return "ScriptingDataSocket"  # a set of identifiers
    return SOCKETS.get(prop.property_type, "ScriptingDataSocket")


def socket_attrs(prop) -> dict:
    if prop.property_type != "VECTOR" or prop.vector_type == "BOOLEAN":
        return {}
    if socket_type(prop) == "ScriptingColorSocket":
        return {"use_alpha": prop.vector_size == 4}
    return {"dimension": str(prop.vector_size)}


def default_value(prop):
    """The default as a Python value (for socket defaults)."""
    kind = prop.property_type
    if kind == "BOOLEAN":
        return prop.default_bool
    if kind == "INTEGER":
        return prop.default_int
    if kind == "FLOAT":
        return prop.default_float
    if kind == "VECTOR":
        if prop.vector_type == "BOOLEAN":
            return None
        return tuple(prop.default_vector)
    if kind == "STRING":
        return prop.default_string
    if kind == "ENUM" and not prop.enum_flag and prop.items_function is None:
        return prop.default_enum or next((i.value for i in prop.enum_items), "")
    return None


def owner_expression(found: Found, context="context"):
    """Expression of the data holding the property, or None if it has to be
    connected (a group item, an object that isn't the active one, ...)."""
    if found.kind == "NODE":
        if found.owner.bl_idname == "SNA_Node_Preferences":
            return PREFERENCES.format(context=context)
        return "self"
    if found.kind == "GROUP":
        return None
    attr = CONTEXT_OWNERS.get(found.prop.attach_to)
    return f"{context}.{attr}" if attr else None


def holder(found: Found, owner: str) -> str:
    """Data the property is an attribute of, given the owner expression."""
    if found.kind == "ADDON" and found.prop.in_addon_group:
        return f"{owner}.{addon_attribute()}"
    return owner


# -----------------------------------------------------------------------------
# Definitions
# -----------------------------------------------------------------------------


class DefinitionError(Exception):
    pass


# types whose values Get / Set Functions can change (get_transform, ...)
TRANSFORMABLE = {"BOOLEAN", "INTEGER", "FLOAT", "VECTOR", "STRING"}


def update_nodes(prop_id):
    """The On Property Update nodes of a property."""
    from ..lib.trees import scripting_node_trees, sn_nodes

    result = []
    for tree in sorted(scripting_node_trees(), key=lambda t: t.name):
        for node in sorted(sn_nodes(tree), key=lambda n: n.name):
            if (
                node.bl_idname == "SNA_Node_OnPropertyUpdate"
                and node.prop_id == prop_id
            ):
                result.append(node)
    return result


def callback_names(prop, py) -> list:
    """Module level names the definition of `prop` needs (core/naming)."""
    names = []
    if prop.property_type != "COLLECTION" and update_nodes(prop.id):
        names.append(naming.Symbol("update", f"update_{py}"))
    if prop.property_type == "ENUM" and prop.items_function is not None:
        names.append(naming.Symbol("items", f"{py}_items"))
        names.append(naming.Symbol("items_cache", f"_{py}_items"))
    if (
        prop.property_type == "POINTER"
        and not prop.uses_group
        and prop.poll_function is not None
    ):
        names.append(naming.Symbol("poll", f"poll_{py}"))
    if prop.property_type == "STRING" and prop.search_function is not None:
        names.append(naming.Symbol("search", f"search_{py}"))
    if prop.property_type in TRANSFORMABLE:
        if prop.get_function is not None:
            names.append(naming.Symbol("get", f"get_{py}"))
        if prop.set_function is not None:
            names.append(naming.Symbol("set", f"set_{py}"))
    return names


def _call(module, tree):
    """Call expression of a function tree's function from `module`, with the
    import inside the function body (properties.py <-> tree modules would
    import each other at module level)."""
    if tree.module_name == module:
        return tree.function_name, []
    line = f"from .{tree.module_name} import {tree.function_name}"
    if module == PROPERTIES_MODULE and tree.module_name in _module_imports.importable:
        _module_imports.lines.add(line)  # no cycle: at the top
        return tree.function_name, []
    return tree.function_name, [line]


class Definition:
    """`bpy.props.X(...)` of one property plus the module level functions it
    needs (written before the class or register() using it)."""

    def __init__(self, found: Found, names, module, group_class):
        self.found = found
        self.prop = found.prop
        self.names = names
        self.module = module  # module the code goes into
        self.group_class = group_class  # group -> class name expression
        self.functions: list[str] = []

    def name(self, key):
        return self.names.get(self.prop.id, key)

    def call(self) -> str:
        prop = self.prop
        kind = prop.property_type
        args = [f"name={prop.name!r}"]
        if prop.description:
            args.append(f"description={prop.description!r}")
        builder = getattr(self, f"_{kind.lower()}")
        function, more = builder()
        args += more
        options = {
            flag
            for flag, on in (
                ("HIDDEN", prop.option_hidden),
                ("SKIP_SAVE", prop.option_skip_save),
                ("ANIMATABLE", prop.option_animatable),
                ("LIBRARY_EDITABLE", prop.option_library_editable),
            )
            if on
        }
        if kind == "ENUM" and prop.enum_flag:
            options.add("ENUM_FLAG")
        if options != {"ANIMATABLE"}:
            args.append(f"options={naming_set(options)}")
        update = self._update()
        if update:
            args.append(f"update={update}")
        if kind in TRANSFORMABLE:
            if prop.get_function is not None:
                args.append(f"get_transform={self._get_function()}")
            if prop.set_function is not None:
                args.append(f"set_transform={self._set_function()}")
        return f"bpy.props.{function}({', '.join(args)})"

    # -- per type -----------------------------------------------------------

    def _boolean(self):
        return "BoolProperty", ["default=True"] if self.prop.default_bool else []

    def _limits(self, cast):
        prop, args = self.prop, []
        if prop.use_min:
            args.append(f"min={cast(prop.min_value)!r}")
        if prop.use_max:
            args.append(f"max={cast(prop.max_value)!r}")
        if prop.use_soft_limits:
            args.append(f"soft_min={cast(prop.soft_min)!r}")
            args.append(f"soft_max={cast(prop.soft_max)!r}")
        return args

    def _integer(self):
        prop, args = self.prop, []
        if prop.default_int:
            args.append(f"default={prop.default_int}")
        args += self._limits(int)
        if prop.subtype_int != "NONE":
            args.append(f"subtype={prop.subtype_int!r}")
        return "IntProperty", args

    def _float(self):
        prop, args = self.prop, []
        if prop.default_float:
            args.append(f"default={round(prop.default_float, 6)!r}")
        args += self._limits(float)
        if prop.precision != 3:
            args.append(f"precision={prop.precision}")
        if prop.subtype_float != "NONE":
            args.append(f"subtype={prop.subtype_float!r}")
        if prop.unit != "NONE":
            args.append(f"unit={prop.unit!r}")
        return "FloatProperty", args

    def _vector(self):
        prop, args = self.prop, []
        size = prop.vector_size
        cast = {"FLOAT": lambda v: round(v, 6), "INTEGER": int, "BOOLEAN": bool}[
            prop.vector_type
        ]
        values = tuple(cast(v) for v in prop.default_vector[:size])
        if size != 3:
            args.append(f"size={size}")
        if any(values):
            args.append(f"default={values!r}")
        if prop.vector_type == "BOOLEAN":
            return "BoolVectorProperty", args
        if prop.vector_type == "INTEGER":
            return "IntVectorProperty", args + self._limits(int)
        args += self._limits(float)
        if prop.precision != 3:
            args.append(f"precision={prop.precision}")
        if prop.subtype_vector != "NONE":
            args.append(f"subtype={prop.subtype_vector!r}")
        return "FloatVectorProperty", args

    def _string(self):
        prop, args = self.prop, []
        if prop.default_string:
            args.append(f"default={prop.default_string!r}")
        if prop.maxlen:
            args.append(f"maxlen={prop.maxlen}")
        if prop.subtype_string != "NONE":
            args.append(f"subtype={prop.subtype_string!r}")
        if prop.search_function is not None:
            args.append(f"search={self._search_function()}")
        return "StringProperty", args

    def _enum(self):
        prop = self.prop
        if prop.items_function is not None:
            return "EnumProperty", [f"items={self._items_function()}"]
        items = list(prop.enum_items)
        if not items:
            raise DefinitionError("Add an item")
        values = [item.value for item in items]
        if len(set(values)) != len(values):
            raise DefinitionError("Item identifiers must be unique")
        icons = any(item.icon for item in items)
        rows = []
        for i, item in enumerate(items):
            row = (item.value, item.name, item.description)
            if icons:
                if item.icon and not is_builtin(item.icon):
                    raise DefinitionError(f"Blender has no icon '{item.icon}'")
                row += (item.icon or "NONE", 1 << i if prop.enum_flag else i)
            rows.append(repr(row))
        args = ["items=[\n    " + ",\n    ".join(rows) + ",\n]"]
        if prop.default_enum:
            if prop.default_enum not in values:
                raise DefinitionError(f"Default '{prop.default_enum}' isn't an item")
            default = prop.default_enum
            args.append(
                f"default={{{default!r}}}" if prop.enum_flag else f"default={default!r}"
            )
        return "EnumProperty", args

    def _pointer(self):
        prop = self.prop
        if prop.uses_group:
            return "PointerProperty", [f"type={self._group()}"]
        args = [f"type=bpy.types.{prop.pointer_type}"]
        if prop.poll_function is not None:
            args.append(f"poll={self._poll_function()}")
        return "PointerProperty", args

    def _collection(self):
        return "CollectionProperty", [f"type={self._group()}"]

    def _group(self):
        group = find_group(self.prop.group_id)
        if group is None:
            raise DefinitionError("Pick a group")
        return self.group_class(group)

    # -- callbacks ----------------------------------------------------------

    def _update(self):
        if self.prop.property_type == "COLLECTION":
            return None
        nodes = update_nodes(self.prop.id)
        if not nodes:
            return None
        targets = [(n.id_data, self.names.get(n.id, "function")) for n in nodes]
        if len(targets) == 1 and self.module == PROPERTIES_MODULE:
            tree, function = targets[0]
            if tree.module_name in _module_imports.importable:
                # the function itself, imported at the top of properties.py
                _module_imports.lines.add(f"from .{tree.module_name} import {function}")
                return function
        name = self.name("update")
        lines = []
        for tree, function in targets:
            if tree.module_name != self.module:
                lines.append(f"from .{tree.module_name} import {function}")
        lines += [f"{function}(self, context)" for _, function in targets]
        self.functions.append(
            f"def {name}(self, context):\n" + "".join(f"    {line}\n" for line in lines)
        )
        return name

    def _items_function(self):
        from . import functions

        tree = self.prop.items_function
        name, cache = self.name("items"), self.name("items_cache")
        function, imports = _call(self.module, tree)
        # (identifier, name, description, icon) items (Enum Item nodes with
        # an icon) get the number Blender needs with an icon
        number = "1 << i" if self.prop.enum_flag else "i"
        scope = ", ".join(
            functions.scope_arguments(tree, {"self": "self", "context": "context"})
        )
        body = imports + [
            f"global {cache}",
            f"{cache} = [",
            "    (item, item, '') if isinstance(item, str)",
            f"    else (*item, {number}) if len(item) == 4",
            "    else tuple(item)",
            f"    for i, item in enumerate({function}({scope}) or ())",
            "]",
            f"return {cache}",
        ]
        self.functions.append(
            f"{cache} = []\n\n\n"
            f"def {name}(self, context):\n" + "".join(f"    {line}\n" for line in body)
        )
        return name

    def _poll_function(self):
        from . import functions

        tree = self.prop.poll_function
        name = self.name("poll")
        function, imports = _call(self.module, tree)
        args = ["object"] if functions.parameters(tree) else []
        args += functions.scope_arguments(tree, {"self": "self"})
        body = imports + [f"return bool({function}({', '.join(args)}))"]
        self.functions.append(
            f"def {name}(self, object):\n" + "".join(f"    {line}\n" for line in body)
        )
        return name

    def _search_function(self):
        from . import functions

        tree = self.prop.search_function
        name = self.name("search")
        function, imports = _call(self.module, tree)
        args = ["edit_text"] if functions.parameters(tree) else []
        args += functions.scope_arguments(tree, {"self": "self", "context": "context"})
        args = ", ".join(args)
        body = imports + [f"return [str(item) for item in {function}({args}) or ()]"]
        self.functions.append(
            f"def {name}(self, context, edit_text):\n"
            + "".join(f"    {line}\n" for line in body)
        )
        return name

    def _transform(self, key, signature, value):
        """A get_transform / set_transform callback calling a function with
        the value."""
        from . import functions

        tree = getattr(self.prop, f"{key}_function")
        if not functions.parameters(tree):
            raise DefinitionError(
                f"The {key.title()} Function needs an input for the value"
            )
        name = self.name(key)
        function, imports = _call(self.module, tree)
        args = ", ".join([value, *functions.scope_arguments(tree, {"self": "self"})])
        body = imports + [f"return {function}({args})"]
        self.functions.append(
            f"def {name}({signature}):\n" + "".join(f"    {line}\n" for line in body)
        )
        return name

    def _get_function(self):
        return self._transform("get", "self, value, is_set", "value")

    def _set_function(self):
        return self._transform(
            "set", "self, new_value, current_value, is_set", "new_value"
        )


def naming_set(values) -> str:
    if not values:
        return "set()"
    return "{" + ", ".join(repr(v) for v in sorted(values)) + "}"


def annotation_lines(items, kind, owner, names, module, group_class):
    """(annotations, functions) for the properties of one list. Broken
    definitions are left out and shown in the list."""
    py = python_names(items)
    annotations, functions = [], []
    for prop in items:
        if prop.property_type == "GROUP":
            continue
        definition = Definition(
            Found(prop, kind, owner, items), names, module, group_class
        )
        try:
            call = definition.call()
        except DefinitionError as exc:
            errors.property_errors[prop.id] = str(exc)
            continue
        annotations.append(f"{py[prop.id]}: {call}")
        functions += definition.functions
    return annotations, functions


def node_annotations(node, ctx):
    """Annotations of an Operator / Preferences node's properties. Writes the
    callbacks they need at module level."""
    builder = ctx._builder

    def group_class(group):
        name = builder.names.get(group.id, "class")
        ctx.imports(f"from .{PROPERTIES_MODULE} import {name}")
        return name

    annotations, functions = annotation_lines(
        node.properties,
        "NODE",
        node,
        builder.names,
        builder.tree.module_name,
        group_class,
    )
    for function in functions:
        ctx.module(function)
    return annotations


# -----------------------------------------------------------------------------
# properties.py
# -----------------------------------------------------------------------------


def _group_order(items):
    """Groups ordered so a group comes after the groups it uses."""
    by_id = {g.id: g for g in items}
    ordered, seen = [], set()

    def visit(group, depth=0):
        if group.id in seen or depth > 32:
            return
        seen.add(group.id)
        for member in group.members:
            if member.uses_group:
                used = by_id.get(member.group_id)
                if used is not None:
                    visit(used, depth + 1)
        ordered.append(group)

    for group in items:
        visit(group)
    return ordered


class _ModuleImports:
    """Imports at the top of properties.py while it's written: of tree
    modules that don't import from it (directly or through others), which
    would be an import cycle."""

    importable: set = set()
    lines: set = set()


_module_imports = _ModuleImports()


def module_source(names, importable=frozenset()) -> str | None:
    """Source of properties.py, or None without add-on properties.
    `importable`: tree modules it may import at the top."""
    addon = addon_settings()
    if not len(addon.properties):
        return None
    _module_imports.importable = set(importable)
    _module_imports.lines = set()
    try:
        return _module_source(names, addon)
    finally:
        _module_imports.importable = set()


def _module_source(names, addon):
    module = PROPERTIES_MODULE
    blocks, register, unregister = [], [], []

    def group_class(group):
        return names.get(group.id, "class")

    for group in _group_order(groups()):
        annotations, functions = annotation_lines(
            group.members, "GROUP", group, names, module, group_class
        )
        blocks += functions
        blocks.append(_class(group_class(group), annotations))

    attr = addon_attribute()
    by_type: dict[str, list] = {}
    direct = []
    for prop in addon.properties:
        if prop.property_type == "GROUP":
            continue
        if prop.in_addon_group:
            by_type.setdefault(prop.attach_to, []).append(prop)
        else:
            direct.append(prop)

    py = python_names(addon.properties)
    for attach, props in by_type.items():
        container = names.get("properties", f"container_{attach}")
        lines, functions = [], []
        for prop in props:
            found = Found(prop, "ADDON", None, addon.properties)
            definition = Definition(found, names, module, group_class)
            try:
                lines.append(f"{py[prop.id]}: {definition.call()}")
            except DefinitionError as exc:
                errors.property_errors[prop.id] = str(exc)
                continue
            functions += definition.functions
        blocks += functions
        blocks.append(_class(container, lines))
        register.append(
            f"bpy.types.{attach}.{attr} = bpy.props.PointerProperty(type={container})"
        )
        unregister.append(f"del bpy.types.{attach}.{attr}")

    for prop in direct:
        definition = Definition(
            Found(prop, "ADDON", None, addon.properties), names, module, group_class
        )
        try:
            call = definition.call()
        except DefinitionError as exc:
            errors.property_errors[prop.id] = str(exc)
            continue
        blocks += definition.functions
        target = f"bpy.types.{prop.attach_to}.{py[prop.id]}"
        register.append(f"{target} = {call}")
        unregister.append(f"del {target}")

    imports = "\n".join(sort_imports({"import bpy", *_module_imports.lines}))
    parts = [imports + "\n"] + [block.rstrip("\n") + "\n" for block in blocks]
    parts.append(_function("register", register))
    parts.append(_function("unregister", list(reversed(unregister))))
    return "\n\n".join(parts)


def _class(name, annotations):
    body = annotations or ["pass"]
    return f"class {name}(bpy.types.PropertyGroup):\n" + "".join(
        _indent(line) for line in body
    )


def _function(name, lines):
    return f"def {name}():\n" + "".join(_indent(line) for line in lines or ["pass"])


def _indent(text):
    return "".join(f"    {line}\n" for line in text.split("\n"))


def claim_names(names):
    """Claim the module level names of all properties (core/naming.build)."""
    addon = addon_settings()
    for group in groups():
        names.claim(group.id, naming.Class("class", "PG", group.name))
    attaches = []
    for prop in addon.properties:
        if prop.property_type != "GROUP" and prop.in_addon_group:
            if prop.attach_to not in attaches:
                attaches.append(prop.attach_to)
    for attach in attaches:
        names.claim(
            "properties",
            naming.Class(f"container_{attach}", "PG", f"{attach} properties"),
        )
    for kind, owner, items in lists():
        py = python_names(items)
        for prop in items:
            if prop.property_type == "GROUP":
                continue
            for name in callback_names(prop, py[prop.id]):
                names.claim(prop.id, name)
