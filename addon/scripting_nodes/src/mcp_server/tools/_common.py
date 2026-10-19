"""Lookups, serializers and value conversion shared by the tools.

Nodes are addressed by their id (`node.id`, stable across renames) or by
"<tree>/<node name>". Sockets by their key (the identifier nodes declare,
e.g. "execute", "text") or, if unambiguous, their name; "<key>+" is the
empty "+" socket of a dynamic group (linking it adds an item).
"""

import bpy

from ...core import errors, scheduler
from ...lib.is_sn import is_sn
from ...lib.trees import node_by_id, scripting_node_trees, sn_nodes
from ...nodes.base_node import ScriptingBaseNode
from ...sockets.socket_types import FLOW_SOCKET


class ToolError(ValueError):
    """A mistake in the call: the message tells the agent what to do."""


# -- lookups ----------------------------------------------------------------------


def find_tree(name):
    tree = bpy.data.node_groups.get(name)
    if tree is None or not is_sn(tree):
        names = [t.name for t in scripting_node_trees()]
        raise ToolError(f"No node tree {name!r}. Trees: {names}")
    return tree


def find_node(ref, tree=None):
    """A node by id, "<tree>/<name>", or name within `tree`."""
    if not isinstance(ref, str) or not ref:
        raise ToolError(f"Expected a node id, got {ref!r}")
    node = node_by_id(ref)
    if node is not None:
        return node
    if "/" in ref:
        tree_name, _, name = ref.rpartition("/")
        tree = find_tree(tree_name)
        ref = name
    if tree is not None:
        node = tree.nodes.get(ref)
        if node is not None:
            return node
    raise ToolError(f"No node {ref!r} (use its id or '<tree>/<node name>')")


def node_classes():
    seen, stack = set(), list(ScriptingBaseNode.__subclasses__())
    while stack:
        cls = stack.pop()
        if cls in seen:
            continue
        seen.add(cls)
        stack.extend(cls.__subclasses__())
        if getattr(cls, "sn_renamed_to", None):
            continue  # an old bl_idname (nodes/_renamed.py)
        if getattr(cls, "bl_idname", None) and getattr(cls, "is_registered", False):
            yield cls


def node_class(bl_idname):
    for cls in node_classes():
        if cls.bl_idname == bl_idname:
            return cls
    raise ToolError(
        f"No node type {bl_idname!r}. Use list_node_types (types look like "
        "'SNA_Node_Print')."
    )


def socket_key(socket):
    """How a tool call addresses `socket`."""
    if getattr(socket, "is_dynamic", False):
        return socket.identifier.split("__")[0] + "+"
    return socket.identifier


def find_socket(node, ref, output):
    sockets = list(node.outputs if output else node.inputs)
    kind = "output" if output else "input"
    if not isinstance(ref, str):
        raise ToolError(f"Socket of {node.name!r} must be a key, got {ref!r}")
    if ref.endswith("+"):
        group = ref[:-1]
        for socket in sockets:
            if getattr(socket, "is_dynamic", False) and (
                socket.identifier == group or socket.identifier.startswith(group + "__")
            ):
                return socket
    for socket in sockets:
        if socket.identifier == ref and socket.enabled:
            return socket
    by_name = [s for s in sockets if s.name == ref and s.enabled]
    if len(by_name) == 1:
        return by_name[0]
    keys = [socket_key(s) for s in sockets if s.enabled]
    raise ToolError(
        f"{node.name!r} has no {kind} {ref!r}. Its {kind}s: {keys}"
        + (" (ambiguous name, use the key)" if by_name else "")
    )


def endpoint(text, tree, refs):
    """(node, socket key) of "<node>.<socket>"; <node> is a ref of this call,
    an id or a node name in `tree`."""
    if not isinstance(text, str) or "." not in text:
        raise ToolError(f"Link ends look like 'node.socket', got {text!r}")
    node_ref, _, key = text.rpartition(".")
    node = refs.get(node_ref) or find_node(node_ref, tree)
    return node, key


# -- serializing ----------------------------------------------------------------


def value(val):
    """JSON-friendly version of a Blender value."""
    if val is None or isinstance(val, (bool, int, float, str)):
        return val
    if isinstance(val, bpy.types.ID):
        return val.name
    if isinstance(val, set):
        return sorted(val)
    try:
        return [value(x) for x in val]
    except TypeError:
        return repr(val)


def node_props(node):
    """The node's own settings (not sockets), with values."""
    result = {}
    base = set(bpy.types.Node.bl_rna.properties.keys()) | {"id"}
    for prop in node.bl_rna.properties:
        name = prop.identifier
        if name in base or name.endswith("_id") or prop.is_hidden:
            continue
        if prop.type == "COLLECTION":
            continue
        try:
            result[name] = value(getattr(node, name))
        except Exception:  # noqa: BLE001 - computed properties may fail
            continue
    return result


def socket_info(socket, with_value=True):
    info = {"key": socket_key(socket), "name": socket.name}
    if socket.bl_idname == FLOW_SOCKET:
        info["type"] = f"Flow ({socket.kind.title()})"
    else:
        info["type"] = socket.bl_idname.replace("Scripting", "").replace("Socket", "")
    if socket.is_linked:
        info["linked"] = True
    if getattr(socket, "is_dynamic", False):
        info["adds_item"] = True
    if with_value and not socket.is_output and not socket.is_linked:
        if "value" in socket.bl_rna.properties:
            info["value"] = value(socket.value)
    return info


def node_error(node):
    return errors.node_message(getattr(node, "id", "")) or None


def node_summary(node):
    info = {
        "id": node.id,
        "name": node.name,
        "type": node.bl_idname,
        "location": [round(node.location.x), round(node.location.y)],
    }
    if node.label:
        info["label"] = node.label
    error = node_error(node)
    if error:
        info["error"] = error
    info["inputs"] = [socket_info(s) for s in node.inputs if s.enabled]
    info["outputs"] = [socket_info(s, False) for s in node.outputs if s.enabled]
    props = node_props(node)
    if props:
        info["props"] = props
    return info


def link_text(link):
    def end(node, socket):
        ref = getattr(node, "id", "") or node.name
        return f"{ref}.{socket_key(socket)}"

    text = f"{end(link.from_node, link.from_socket)} -> {end(link.to_node, link.to_socket)}"
    return text + " (muted)" if link.is_muted else text


def tree_info(tree):
    from ...core import functions

    info = {
        "name": tree.name,
        "module": tree.module_file,
        "nodes": sum(1 for _ in sn_nodes(tree)),
    }
    if tree.folder:
        info["folder"] = tree.folder
    if functions.is_function(tree):
        info["function"] = tree.function_name
    return info


# -- setting values ---------------------------------------------------------------


def _data_collection(type_name):
    for prop in bpy.types.BlendData.bl_rna.properties:
        if prop.type == "COLLECTION" and prop.fixed_type.identifier == type_name:
            return getattr(bpy.data, prop.identifier)
    return None


def coerce(prop, raw):
    """`raw` (from JSON) as a value for the RNA property `prop`."""
    kind = prop.type
    if kind == "POINTER":
        if raw is None or raw == "":
            return None
        name = raw.get("name") if isinstance(raw, dict) else raw
        data = _data_collection(prop.fixed_type.identifier)
        target = data.get(name) if data is not None else None
        if target is None:
            raise ToolError(f"No {prop.fixed_type.identifier} named {name!r}")
        return target
    if kind == "ENUM" and prop.is_enum_flag:
        return set(raw if isinstance(raw, (list, tuple, set)) else [raw])
    if getattr(prop, "is_array", False) or getattr(prop, "array_length", 0) > 0:
        size = prop.array_length
        if not isinstance(raw, (list, tuple)):
            return [raw] * size
        # vectors are stored with room for 4 values (their size is a setting)
        current = list(prop.default_array) if hasattr(prop, "default_array") else []
        padded = list(raw) + current[len(raw) : size] + [0] * size
        return padded[:size]
    if isinstance(raw, str):
        if kind == "BOOLEAN":
            return raw.strip().lower() in ("true", "1", "yes")
        if kind == "INT":
            return int(raw)
        if kind == "FLOAT":
            return float(raw)
    return raw


def set_rna(owner, name, raw):
    """Set an RNA property of `owner` from a JSON value."""
    prop = owner.bl_rna.properties.get(name)
    if prop is None:
        raise ToolError(f"{owner.bl_rna.identifier} has no setting {name!r}")
    if prop.is_readonly:
        raise ToolError(f"{name!r} can't be changed")
    try:
        setattr(owner, name, coerce(prop, raw))
    except (TypeError, ValueError) as exc:
        hint = ""
        if prop.type == "ENUM":
            hint = f" Options: {[i.identifier for i in prop.enum_items]}"
        raise ToolError(f"Can't set {name!r} to {raw!r}: {exc}.{hint}") from exc


def flush():
    scheduler.flush()


def mark(node):
    if hasattr(node, "mark_dirty"):
        node.mark_dirty()
    references_changed()


def references_changed():
    scheduler.request_full()
