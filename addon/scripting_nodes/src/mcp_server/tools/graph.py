"""Node trees and nodes: what types there are, reading trees, and editing
them in batches (add, change, link, delete in one call)."""

import inspect

import bpy

from ...blend_data import rna
from ...core import compiler, properties, references
from ...lib.trees import sn_nodes
from ...nodes.categories.categories import category_label
from . import Later, tool
from ._common import (
    ToolError,
    endpoint,
    find_node,
    find_socket,
    find_tree,
    flush,
    link_text,
    mark,
    node_class,
    node_classes,
    node_summary,
    set_rna,
    socket_info,
    tree_info,
)

_SCRATCH = "__sn_mcp_scratch__"


def _category(cls):
    parts = (cls.__module__ or "").split(".")
    if "categories" in parts:
        i = parts.index("categories")
        if i + 1 < len(parts):
            return category_label(parts[i + 1])
    return ""


def _doc(cls):
    return " ".join((inspect.getdoc(cls) or "").split())


@tool(
    "list_node_types",
    """Node types by category, with what each does. Filter by category or by
    words in the name and description.""",
    {
        "category": {"type": "string"},
        "search": {"type": "string", "description": "Words to look for"},
    },
)
def list_node_types(category="", search=""):
    words = search.lower().split()
    result = {}
    for cls in node_classes():
        cat = _category(cls)
        if category and cat.lower() != category.lower():
            continue
        text = f"{cls.bl_label} {_doc(cls)}".lower()
        if any(word not in text for word in words):
            continue
        result.setdefault(cat, []).append(
            {"type": cls.bl_idname, "label": cls.bl_label, "doc": _doc(cls)[:160]}
        )
    for entries in result.values():
        entries.sort(key=lambda e: e["label"])
    return {"categories": dict(sorted(result.items()))}


def _prop_info(prop):
    info = {"name": prop.identifier, "type": prop.type.lower()}
    if prop.description:
        info["description"] = prop.description
    if prop.type == "ENUM":
        info["options"] = [i.identifier for i in prop.enum_items]
    return info


@tool(
    "get_node_type",
    """Everything about a node type: what it does, its sockets (keys to link
    and set), its settings with their options, the nodes it can point at
    (references) and property pickers. Sockets of some nodes change with
    their settings.""",
    {"type": {"type": "string", "description": "e.g. SNA_Node_Print"}},
    required=["type"],
)
def get_node_type(type):
    cls = node_class(type)
    scratch = bpy.data.node_groups.new(_SCRATCH, "ScriptingNodeTree")
    try:
        node = scratch.nodes.new(cls.bl_idname)
        info = node_summary(node)
        base = set(bpy.types.Node.bl_rna.properties.keys()) | {"id"}
        settings = [
            _prop_info(p)
            for p in node.bl_rna.properties
            if p.identifier not in base
            and not p.identifier.endswith("_id")
            and not p.is_hidden
            and p.type != "COLLECTION"
        ]
        refs = {
            attr: sorted(field.types) for attr, field in references.fields(node).items()
        }
        pickers = dict(getattr(node, "sn_property_references", {}))
    finally:
        bpy.data.node_groups.remove(scratch)
    result = {
        "type": cls.bl_idname,
        "label": cls.bl_label,
        "category": _category(cls),
        "doc": _doc(cls),
        "inputs": info["inputs"],
        "outputs": info["outputs"],
        "settings": settings,
    }
    if refs:
        result["references"] = {
            attr: f"set to a node id of: {types}" for attr, types in refs.items()
        }
    if pickers:
        result["property_pickers"] = {
            attr: f"set to a property name or id ({kind})"
            for attr, kind in pickers.items()
        }
    if getattr(cls, "sn_root", False):
        result["root"] = "Runs on its own (no flow input needed)"
    return result


@tool(
    "create_tree",
    """A new node tree. Each tree becomes a module of the add-on. To make it
    a function (node group), give it inputs/outputs, see edit_function.""",
    {"name": {"type": "string"}},
    required=["name"],
    writes=True,
)
def create_tree(name):
    if bpy.data.node_groups.get(name) is not None:
        raise ToolError(f"A node tree {name!r} exists already")
    tree = bpy.data.node_groups.new(name, "ScriptingNodeTree")
    from ...core import scheduler

    scheduler.request_full()
    flush()
    return tree_info(tree)


@tool(
    "get_tree",
    """A node tree: its nodes (id, type, sockets with keys and values,
    settings, errors) and links ('node.socket -> node.socket').""",
    {"tree": {"type": "string"}},
    required=["tree"],
)
def get_tree(tree):
    tree = find_tree(tree)
    return {
        **tree_info(tree),
        "nodes": [node_summary(n) for n in sn_nodes(tree)]
        + [
            _interface_node(n)
            for n in tree.nodes
            if n.bl_idname.startswith("NodeGroup")
        ],
        "links": [link_text(link) for link in tree.links],
    }


def _interface_node(node):
    return {
        "id": node.name,
        "name": node.name,
        "type": node.bl_idname,
        "location": [round(node.location.x), round(node.location.y)],
        "inputs": [socket_info(s, False) for s in node.inputs],
        "outputs": [socket_info(s, False) for s in node.outputs],
    }


@tool(
    "get_node",
    """One node in detail: sockets, settings, what it does, the code it wrote
    in the last build, its error, the nodes and properties it points at (with
    the choices) and which nodes point at it.""",
    {"node": {"type": "string", "description": "Node id or '<tree>/<name>'"}},
    required=["node"],
)
def get_node(node):
    node = find_node(node)
    info = node_summary(node)
    info["tree"] = node.id_data.name
    info["doc"] = _doc(type(node))
    code = compiler.node_lines.get(node.id)
    if code:
        info["code"] = "\n".join(code)
    refs = {}
    for attr, field in references.fields(node).items():
        target = references.resolve(node, attr)
        refs[attr] = {
            "target": target.id if target else None,
            "choices": [
                {"id": n.id, "name": n.name, "tree": n.id_data.name}
                for _, n in field.choices(node)
            ],
        }
    if refs:
        info["references"] = refs
    pickers = {}
    for attr, category in getattr(node, "sn_property_references", {}).items():
        found = properties.find(getattr(node, attr + "_id", ""))
        pickers[attr] = {
            "property": found.prop.name if found else None,
            "choices": [text for text, _ in properties.choices(category)],
        }
    if pickers:
        info["property_pickers"] = pickers
    users = references.users(node)
    if users:
        info["used_by"] = [{"node": n.id, "field": attr} for n, attr in users]
    return info


# -- editing ------------------------------------------------------------------------


def _set_prop(node, name, raw, refs):
    if name == "paste_path" and hasattr(node, "paste_path"):
        try:
            node.paste_path(raw)
        except ValueError as exc:
            raise ToolError(f"Can't use the path {raw!r}: {exc}") from exc
        return
    if name in references.fields(node):
        target = None
        if raw:
            target = refs.get(raw) or find_node(raw, node.id_data)
        references.point(node, name, target)
        return
    if name == "operator_blender" and raw:
        # the picker's text, "<label>  [<idname>]", from an idname
        from ...nodes._operator_call import blender_operator_display

        idname = raw.rsplit("[", 1)[-1].rstrip("]") if raw.endswith("]") else raw
        display = blender_operator_display(idname)
        if not display:
            raise ToolError(
                f"No Blender operator {idname!r} (e.g. 'mesh.primitive_cube_add')"
            )
        if getattr(node, "mode", "") == "CUSTOM":
            node.mode = "BLENDER"
        node.operator_blender = display
        mark(node)
        return
    pickers = getattr(node, "sn_property_references", {})
    if name in pickers:
        setattr(
            node, name + "_id", _find_property(raw, pickers[name]).id if raw else ""
        )
        mark(node)
        return
    set_rna(node, name, raw)


def _find_property(ref, category):
    """A property by id or name (the label shown in pickers)."""
    found = properties.find(ref)
    if found is not None:
        return found.prop
    choices = properties.choices(category)
    for text, prop in choices:
        if ref in (text, prop.name):
            return prop
    raise ToolError(
        f"No property {ref!r} to pick here. Choices: {[t for t, _ in choices]}"
    )


def _set_input(node, key, raw):
    socket = find_socket(node, key, output=False)
    if socket.is_linked:
        raise ToolError(f"{node.name}.{key} is linked: its value comes from the link")
    if "value" not in socket.bl_rna.properties:
        raise ToolError(f"{node.name}.{key} has no value to set (link it instead)")
    set_rna(socket, "value", raw)


def _link_pair(item):
    if isinstance(item, (list, tuple)) and len(item) == 2:
        return item
    if isinstance(item, dict) and "from" in item and "to" in item:
        return item["from"], item["to"]
    raise ToolError(f"A link is ['node.socket', 'node.socket'], got {item!r}")


@tool(
    "edit_tree",
    """Change a node tree in one call, in this order: add nodes, change
    nodes, delete nodes, link, unlink. Nodes are addressed by id, by name, or
    by the `ref` you give a node you add in this call.

    add: [{"ref": "op", "type": "SNA_Node_Operator", "location": [x, y],
    "label": "...", "props": {...}, "inputs": {"label": "Say Hi"}}]
    edit: [{"node": "<id>", "props": {...}, "inputs": {...}, "location": [..]}]
    link / unlink: [["op.execute", "print.flow"], ...] (output -> input)

    props are the node's settings (get_node_type lists them); references to
    other nodes take a node id or ref; property pickers take a property name;
    Blender Data nodes take "paste_path": "bpy.context.scene.render.fps".
    inputs set the values of unlinked input sockets, by key. "key+" is the
    "+" socket of a growing group: linking it adds an item. Returns the ids
    of added nodes and the changed nodes with their errors.""",
    {
        "tree": {"type": "string"},
        "add": {"type": "array", "items": {"type": "object"}},
        "edit": {"type": "array", "items": {"type": "object"}},
        "delete": {"type": "array", "items": {"type": "string"}},
        "link": {"type": "array"},
        "unlink": {"type": "array"},
        "rename": {"type": "string", "description": "New name of the tree"},
    },
    required=["tree"],
    writes=True,
)
def edit_tree(tree, add=(), edit=(), delete=(), link=(), unlink=(), rename=""):
    tree = find_tree(tree)
    added = []
    try:
        return _edit_tree(tree, added, add, edit, delete, link, unlink, rename)
    except Exception as exc:
        # leave no half-built nodes: remove what this call added
        for node in added:
            try:
                tree.nodes.remove(node)
            except (ReferenceError, RuntimeError):
                pass  # deleted in this call
        flush()
        if added:
            raise ToolError(f"{exc} (the nodes this call added were removed)") from exc
        raise


def _edit_tree(tree, added, add, edit, delete, link, unlink, rename):
    refs, touched = {}, []

    # add
    for spec in add:
        node_type = spec.get("type")
        node_class(node_type)
        node = tree.nodes.new(node_type)
        added.append(node)
        if "location" in spec:
            node.location = spec["location"]
        if spec.get("name"):
            node.name = spec["name"]
        if spec.get("label"):
            node.label = spec["label"]
        refs[spec.get("ref") or node.name] = node
        touched.append((node, spec))
    for spec in edit:
        node = refs.get(spec.get("node")) or find_node(spec.get("node"), tree)
        if node.id_data is not tree:
            raise ToolError(f"{node.name!r} is in tree {node.id_data.name!r}")
        if "location" in spec:
            node.location = spec["location"]
        if "label" in spec:
            node.label = spec["label"]
        touched.append((node, spec))
    for node, spec in touched:
        for name, raw in (spec.get("props") or {}).items():
            _set_prop(node, name, raw, refs)
    flush()  # settings can change sockets

    deleted = []
    for ref in delete:
        node = refs.pop(ref, None) or find_node(ref, tree)
        deleted.append(node.name)
        touched = [(n, s) for n, s in touched if n != node]
        tree.nodes.remove(node)

    for item in link:
        source, target = _link_pair(item)
        from_node, from_key = endpoint(source, tree, refs)
        to_node, to_key = endpoint(target, tree, refs)
        tree.links.new(
            find_socket(from_node, from_key, output=True),
            find_socket(to_node, to_key, output=False),
        )
        tree.update()
        flush()  # "+" sockets grow one at a time
    for item in unlink:
        source, target = _link_pair(item)
        from_node, from_key = endpoint(source, tree, refs)
        to_node, to_key = endpoint(target, tree, refs)
        out = find_socket(from_node, from_key, output=True)
        inp = find_socket(to_node, to_key, output=False)
        found = [
            lk for lk in tree.links if lk.from_socket == out and lk.to_socket == inp
        ]
        if not found:
            raise ToolError(f"No link {source} -> {target}")
        tree.links.remove(found[0])
        tree.update()
    flush()

    for node, spec in touched:
        for key, raw in (spec.get("inputs") or {}).items():
            _set_input(node, key, raw)
        mark(node)
    if rename:
        tree.name = rename
    flush()

    result = {"tree": tree.name}
    if refs:
        result["added"] = {ref: node.id for ref, node in refs.items()}
    result["nodes"] = [node_summary(node) for node, _ in touched]
    if deleted:
        result["deleted"] = deleted
    return result


@tool(
    "search_data_paths",
    """Find Blender data paths for Blender Data nodes and property fields:
    words like 'render fps' or 'active material'. root: CONTEXT (what the
    user works on: scene, active_object, ...) or DATA (all of the file).""",
    {
        "query": {"type": "string"},
        "root": {"type": "string", "enum": ["CONTEXT", "DATA"]},
    },
    required=["query"],
)
def search_data_paths(query, root="CONTEXT"):
    step = rna.root_step(rna.ROOT_TYPES[root])
    entries = rna.search(step, query, limit=25)
    prefix = "bpy.context." if root == "CONTEXT" else "bpy.data."
    return {
        "paths": [
            {"path": prefix + e.path, "text": e.text, "type": e.type_label}
            for e in entries
        ]
    }


@tool(
    "show_tree",
    """Open a node tree in the node editor, framed (and a node selected), so
    the user sees it - and a screenshot shows it.""",
    {
        "tree": {"type": "string"},
        "node": {"type": "string", "description": "Node to select and frame"},
    },
)
def show_tree(tree, node=""):
    from .blender import _area, _window, override, tag_redraw

    tree = find_tree(tree)
    window = _window()
    if window is None or bpy.app.background:
        raise ToolError("Blender has no window")
    area = _area(window, "NODE_EDITOR")
    space = area.spaces.active
    space.tree_type = "ScriptingNodeTree"
    space.node_tree = tree
    target = find_node(node, tree) if node else None
    for each in tree.nodes:
        each.select = each == target
    if target is not None:
        tree.nodes.active = target
    tag_redraw()

    def frame():
        # once drawn, nodes have their size
        with override("NODE_EDITOR"):
            if target is not None:
                bpy.ops.node.view_selected()
            else:
                bpy.ops.node.view_all()
        tag_redraw()
        return {"tree": tree.name, "node": target.id if target else None}

    return Later(frame)
