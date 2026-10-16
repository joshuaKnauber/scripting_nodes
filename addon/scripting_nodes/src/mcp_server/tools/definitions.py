"""Property lists (the add-on's, groups', Operator / Preferences nodes')
and function interfaces (the inputs and outputs of node groups)."""

import contextlib

import bpy

from ...core import errors, functions, properties, scheduler
from ...sockets.socket_types import DATA_SOCKET_LABELS, FLOW_SOCKET
from . import tool
from ._common import ToolError, find_node, find_tree, flush, set_rna

TYPES = ["BOOLEAN", "INTEGER", "FLOAT", "VECTOR", "STRING", "ENUM", "POINTER"]
TYPES += ["COLLECTION", "GROUP"]
DEFAULTS = {
    "BOOLEAN": "default_bool",
    "INTEGER": "default_int",
    "FLOAT": "default_float",
    "VECTOR": "default_vector",
    "STRING": "default_string",
    "ENUM": "default_enum",
}
# interface socket type names -> (socket idname, flow kind)
SOCKET_TYPES = {"Program": (FLOW_SOCKET, "PROGRAM"), "Logic": (FLOW_SOCKET, "LOGIC")}
SOCKET_TYPES["Interface"] = (FLOW_SOCKET, "INTERFACE")
SOCKET_TYPES.update(
    {
        label.replace(" ", ""): (idname, None)
        for idname, label in DATA_SOCKET_LABELS.items()
    }
)


# -- properties -------------------------------------------------------------------


def _owner(owner):
    """(items, owner object, kind) of a property list: "addon", a group
    ("group:Name" or its name / id) or an Operator / Preferences node."""
    addon = bpy.context.scene.sna.addon
    if owner in ("", "addon", None):
        return addon.properties, None, "ADDON"
    name = owner.removeprefix("group:")
    for group in properties.groups():
        if name in (group.name, group.id):
            return group.members, group, "GROUP"
    try:
        node = find_node(owner)
    except ToolError:
        groups = [g.name for g in properties.groups()]
        raise ToolError(
            f"No property list {owner!r}: 'addon', a group {groups} or the id "
            "of an Operator / Preferences node"
        ) from None
    if not hasattr(node, "properties"):
        raise ToolError(f"{node.name!r} has no properties (Operator, Preferences)")
    return node.properties, node, "NODE"


def _find(items, ref):
    for prop in items:
        if ref in (prop.id, prop.name):
            return prop
    raise ToolError(f"No property {ref!r}. Here: {[p.name for p in items]}")


def _configure(prop, settings, kind):
    for key, raw in settings.items():
        if key in ("name", "type", "property"):
            continue
        if key == "default":
            attr = DEFAULTS.get(prop.property_type)
            if attr is None:
                raise ToolError(f"{prop.property_type} properties have no default")
            if attr == "default_vector":
                raw = (list(raw) + [0.0] * 4)[:4]
            set_rna(prop, attr, raw)
        elif key == "items":
            prop.enum_items.clear()
            for entry in raw:
                item = prop.enum_items.add()
                if isinstance(entry, str):
                    item.name = entry
                else:
                    for attr in ("name", "identifier", "description", "icon"):
                        if attr in entry:
                            setattr(item, attr, entry[attr])
        elif key == "group":
            group = next(
                (g for g in properties.groups() if raw in (g.name, g.id)), None
            )
            if group is None:
                names = [g.name for g in properties.groups()]
                raise ToolError(f"No group {raw!r}. Groups: {names}")
            prop.group_id = group.id
            if prop.property_type == "POINTER":
                prop.pointer_source = "GROUP"
        elif key == "on":
            if kind != "ADDON":
                raise ToolError("Only add-on properties are attached ('on')")
            set_rna(prop, "attach_to", raw)
        elif key in ("items_function", "poll_function", "search_function"):
            set_rna(prop, key, find_tree(raw).name if raw else None)
        else:
            set_rna(prop, key, raw)


def _listing(items):
    result = []
    for prop in items:
        entry = {"name": prop.name, "id": prop.id, "type": prop.property_type}
        error = errors.property_errors.get(prop.id)
        if error:
            entry["error"] = error
        result.append(entry)
    return result


@tool(
    "edit_properties",
    """Add, change or remove property definitions of a list: the add-on's
    ("addon": stored on the scene by default, `on` picks Object, ...), a
    group's ("group:<name>", a GROUP is a list of its own, used by POINTER /
    COLLECTION properties) or an Operator / Preferences node's (its id).

    add: [{"name": "Count", "type": "INTEGER", "default": 3, ...settings}]
    types: BOOLEAN INTEGER FLOAT VECTOR STRING ENUM POINTER COLLECTION GROUP.
    Settings: default; items (ENUM: names or {name, identifier,
    description, icon}); group (POINTER / COLLECTION of a group); on (attach
    type); description, subtype_float, unit, use_min, min_value, use_max,
    max_value, use_soft_limits, soft_min, soft_max, vector_size,
    vector_type, maxlen, subtype_string, pointer_type, enum_flag,
    python_name, items_function / poll_function / search_function (a
    function tree).
    edit: [{"property": "Count", "name": "Amount", ...settings}]
    remove: ["Amount"]

    Fields and Get / Set Property nodes pick properties by name.""",
    {
        "owner": {"type": "string", "description": "'addon', 'group:<name>', node id"},
        "add": {"type": "array", "items": {"type": "object"}},
        "edit": {"type": "array", "items": {"type": "object"}},
        "remove": {"type": "array", "items": {"type": "string"}},
    },
    required=["owner"],
    writes=True,
)
def edit_properties(owner, add=(), edit=(), remove=()):
    items, holder, kind = _owner(owner)
    for spec in add:
        prop_type = spec.get("type", "FLOAT")
        if prop_type not in TYPES:
            raise ToolError(f"Unknown type {prop_type!r}. Types: {TYPES}")
        if prop_type == "GROUP" and kind != "ADDON":
            raise ToolError("Groups are add-on properties (owner 'addon')")
        if not spec.get("name"):
            raise ToolError("A new property needs a name")
        prop = items.add()
        prop.init(spec["name"], prop_type)
        prop_id = prop.id
        # adding can move items in memory: look it up again
        _configure(_find(items, prop_id), spec, kind)
    for spec in edit:
        prop = _find(items, spec.get("property", ""))
        _configure(prop, spec, kind)
        if spec.get("name"):
            prop.name = spec["name"]
    for ref in remove:
        prop = _find(items, ref)
        items.remove(list(items).index(prop))
    if holder is not None and hasattr(holder, "mark_dirty"):
        holder.mark_dirty()
    scheduler.request_full()
    flush()
    return {"owner": owner or "addon", "properties": _listing(_owner(owner)[0])}


# -- functions ---------------------------------------------------------------------


def _socket_type(name):
    if name not in SOCKET_TYPES:
        raise ToolError(f"Unknown socket type {name!r}. Types: {list(SOCKET_TYPES)}")
    return SOCKET_TYPES[name]


def _interface(tree):
    result = {"inputs": [], "outputs": []}
    for item in tree.interface.items_tree:
        if item.item_type != "SOCKET":
            continue
        if item.bl_socket_idname == FLOW_SOCKET:
            kind = item.kind.title()
        else:
            kind = DATA_SOCKET_LABELS.get(item.bl_socket_idname, "").replace(" ", "")
        key = "inputs" if item.in_out == "INPUT" else "outputs"
        result[key].append({"name": item.name, "type": kind, "key": item.identifier})
    return result


def _ensure_io_nodes(tree):
    if not any(n.bl_idname == functions.GROUP_INPUT for n in tree.nodes):
        tree.nodes.new(functions.GROUP_INPUT).location = (-400, 0)
    if not any(n.bl_idname == functions.GROUP_OUTPUT for n in tree.nodes):
        tree.nodes.new(functions.GROUP_OUTPUT).location = (400, 0)


@tool(
    "edit_function",
    """Make a node tree a function (node group) or change its inputs and
    outputs. Data inputs are its parameters, data outputs what it returns.
    A Program flow input makes it a statement (its body starts at Group
    Input's flow, the flow output is where the caller continues), an
    Interface flow input draws UI, no flow sockets: a pure function used as
    a value. Group Input / Group Output nodes are added; link their sockets
    (keys from get_tree) with edit_tree. Call it with a Group node
    (props: {"node_tree": "<tree>"}).

    add: [{"name": "Value", "type": "Float", "output": false}]
    types: Program Logic Interface (flows) and Data BlendData String Boolean
    Float Integer Vector Color List Icon.
    rename: {"Value": "Amount"}; remove: ["Amount"]""",
    {
        "tree": {"type": "string"},
        "add": {"type": "array", "items": {"type": "object"}},
        "rename": {"type": "object"},
        "remove": {"type": "array", "items": {"type": "string"}},
    },
    required=["tree"],
    writes=True,
)
def edit_function(tree, add=(), rename=None, remove=()):
    tree = find_tree(tree)
    items = [i for i in tree.interface.items_tree if i.item_type == "SOCKET"]
    for name in remove:
        item = next((i for i in items if i.name == name), None)
        if item is None:
            raise ToolError(f"No input or output {name!r}")
        tree.interface.remove(item)
    for old, new in (rename or {}).items():
        item = next((i for i in tree.interface.items_tree if i.name == old), None)
        if item is None:
            raise ToolError(f"No input or output {old!r}")
        item.name = new
    for spec in add:
        idname, kind = _socket_type(spec.get("type", "Data"))
        in_out = "OUTPUT" if spec.get("output") else "INPUT"
        item = tree.interface.new_socket(
            spec.get("name", "Value"), in_out=in_out, socket_type=idname
        )
        if kind is not None:
            item.kind = kind
    _ensure_io_nodes(tree)
    tree.update()
    scheduler.request_full()
    flush()
    result = {"tree": tree.name, **_interface(tree)}
    if functions.is_function(tree):
        result["function"] = tree.function_name
        problem = functions.problem(tree)
        if problem:
            result["problem"] = problem
    return result


@contextlib.contextmanager
def _node_editor(tree):
    """A node editor showing `tree`, overriding the context (the group
    operators work in one). Without one on screen, an area is one for the
    call."""
    from .blender import _window

    window = _window()
    if window is None or bpy.app.background:
        raise ToolError("Making groups needs Blender with a window (node editor)")
    areas = window.screen.areas
    editors = [a for a in areas if a.type == "NODE_EDITOR"]
    area = editors[0] if editors else max(areas, key=lambda a: a.width * a.height)
    old_type = area.type
    area.type = "NODE_EDITOR"
    space = area.spaces.active
    old_tree_type, old_tree = space.tree_type, space.node_tree
    space.tree_type = "ScriptingNodeTree"
    space.node_tree = tree
    region = next(r for r in area.regions if r.type == "WINDOW")
    try:
        with bpy.context.temp_override(
            window=window, area=area, region=region, space_data=space
        ):
            yield
    finally:
        if not editors:
            space.tree_type = old_tree_type
            if old_tree_type == "ScriptingNodeTree":
                space.node_tree = old_tree
            area.type = old_type


@tool(
    "make_group",
    """Move nodes into a new function (node group) and call it from where
    they were, like Ctrl G: links crossing the selection become the
    function's inputs and outputs. Needs Blender with a window.""",
    {
        "tree": {"type": "string"},
        "nodes": {"type": "array", "items": {"type": "string"}},
        "name": {"type": "string", "description": "Name of the new function"},
    },
    required=["tree", "nodes"],
    writes=True,
)
def make_group(tree, nodes, name=""):
    from ._common import node_summary

    parent = find_tree(tree)
    moved = [find_node(ref, parent) for ref in nodes]
    if any(node.id_data != parent for node in moved):
        raise ToolError(f"All nodes must be in {parent.name!r}")
    before = {n.as_pointer() for n in parent.nodes}
    for node in parent.nodes:
        node.select = node in moved
    with _node_editor(parent):
        bpy.ops.sna.make_group()
    call = next(n for n in parent.nodes if n.as_pointer() not in before)
    group = call.node_tree
    if name:
        group.name = name
    flush()
    return {
        "function": {"tree": group.name, **_interface(group)},
        "group_node": node_summary(call),
    }


@tool(
    "ungroup",
    """Put the nodes of a Group node back into its tree, like Ctrl Alt G
    (the function stays). Needs Blender with a window.""",
    {"node": {"type": "string", "description": "The Group node"}},
    required=["node"],
    writes=True,
)
def ungroup(node):
    call = find_node(node)
    if call.bl_idname != "SNA_Node_Group" or call.node_tree is None:
        raise ToolError(f"{call.name!r} isn't a Group node calling a function")
    parent = call.id_data
    before = {n.as_pointer() for n in parent.nodes}
    for each in parent.nodes:
        each.select = each == call
    with _node_editor(parent):
        bpy.ops.sna.ungroup()
    flush()
    added = [n for n in parent.nodes if n.as_pointer() not in before]
    return {"tree": parent.name, "nodes": [n.id for n in added if hasattr(n, "id")]}
