"""MCP tool definitions for Scripting Nodes.

Every tool runs on Blender's main thread via `bridge.call_on_main` and
returns JSON-serializable data.
"""

import inspect
import os

import bpy

from ...lib.utils.is_sn import is_sn
from ...lib.utils.node_tree.scripting_node_trees import (
    node_by_id,
    scripting_node_trees,
    sn_nodes,
)
from ..nodes.base_node import ScriptingBaseNode
from ..node_tree.code_gen.generators.node_tree import code_gen_node_tree


_READ_MAX_LINES = 300
_READ_DEFAULT_LINES = 100

# code/id fields on ScriptingBaseNode — the `code` block of get_node already
# exposes them, so they're noise inside `props`.
_INTERNAL_PROPS = {
    "id",
    "code_imports",
    "code_module",
    "code_inline",
    "code_global",
    "code_register",
    "code_unregister",
}

# bl_rna identifier -> bpy.data collection name.
_BPY_DATA_COLLECTIONS = {
    "Action": "actions",
    "Armature": "armatures",
    "Brush": "brushes",
    "Camera": "cameras",
    "Collection": "collections",
    "Curve": "curves",
    "Image": "images",
    "Lattice": "lattices",
    "Light": "lights",
    "Material": "materials",
    "Mesh": "meshes",
    "Metaball": "metaballs",
    "NodeTree": "node_groups",
    "Object": "objects",
    "Scene": "scenes",
    "Text": "texts",
    "Texture": "textures",
    "World": "worlds",
}


# --- lookup helpers ---------------------------------------------------------


def _require_node(node_id):
    node = node_by_id(node_id)
    if node is None:
        raise ValueError(f"No node with id {node_id!r}")
    return node


def _find_tree(name):
    ntree = bpy.data.node_groups.get(name)
    if ntree is None or not is_sn(ntree):
        raise ValueError(f"No scripting node tree named {name!r}")
    return ntree


def _socket_by_name(node, kind, name):
    sockets = list(node.inputs if kind == "input" else node.outputs)
    if kind not in ("input", "output"):
        raise ValueError(f"kind must be 'input' or 'output', got {kind!r}")
    matches = [(i, s) for i, s in enumerate(sockets) if s.name == name]
    if not matches:
        raise ValueError(
            f"Node {node.name!r} has no {kind} socket named {name!r}. "
            f"Available: {[s.name for s in sockets]}"
        )
    if len(matches) > 1:
        raise ValueError(
            f"Node {node.name!r} has {len(matches)} {kind} sockets named "
            f"{name!r} (indices {[i for i, _ in matches]}) — ambiguous"
        )
    return matches[0][1]


def _resolve_link_endpoints(from_node_id, from_socket, to_node_id, to_socket):
    src_node = _require_node(from_node_id)
    dst_node = _require_node(to_node_id)
    if src_node.id_data is not dst_node.id_data:
        raise ValueError("Endpoints live in different node trees")
    src = _socket_by_name(src_node, "output", from_socket)
    dst = _socket_by_name(dst_node, "input", to_socket)
    return src_node, src, dst_node, dst, src_node.id_data


def _iter_sn_node_classes():
    seen = set()
    stack = list(ScriptingBaseNode.__subclasses__())
    while stack:
        cls = stack.pop()
        if cls in seen:
            continue
        seen.add(cls)
        if getattr(cls, "bl_idname", None):
            yield cls
        stack.extend(cls.__subclasses__())


def _category_for_class(cls):
    parts = (cls.__module__ or "").split(".")
    try:
        i = parts.index("categories")
    except ValueError:
        return ""
    return parts[i + 1] if i + 1 < len(parts) else ""


# --- serializers ------------------------------------------------------------


def _sn_prop_names(node):
    # SN-declared bpy props (PEP 526 class-level metadata is filtered by the
    # _PropertyDeferred check). Walks MRO up to and including ScriptingBaseNode.
    names = []
    seen = set(_INTERNAL_PROPS)
    for cls in type(node).__mro__:
        for k, v in (cls.__dict__.get("__annotations__") or {}).items():
            if k in seen or not isinstance(v, bpy.props._PropertyDeferred):
                continue
            seen.add(k)
            names.append(k)
        if cls is ScriptingBaseNode:
            break
    return names


def _serialize_value(val):
    if val is None or isinstance(val, (bool, int, float, str)):
        return val
    if isinstance(val, bpy.types.ID):
        return {"_ref": type(val).__name__, "name": val.name}
    try:
        return [_serialize_value(x) for x in val]
    except TypeError:
        return repr(val)


def _serialize_props(node):
    out = {}
    for name in _sn_prop_names(node):
        try:
            out[name] = _serialize_value(getattr(node, name))
        except Exception as exc:
            out[name] = {"_error": f"{type(exc).__name__}: {exc}"}
    return out


def _serialize_socket(socket):
    info = {
        "name": socket.name,
        "bl_idname": socket.bl_idname,
        "is_linked": socket.is_linked,
    }
    if getattr(socket, "label", ""):
        info["label"] = socket.label
    if getattr(socket, "socket_type", None) is not None:
        info["socket_type"] = socket.socket_type
    if not socket.is_output and "value" in getattr(socket.bl_rna, "properties", {}):
        try:
            info["value"] = _serialize_value(socket.value)
        except Exception:
            pass
    return info


def _node_ref(node):
    return {
        "sn_id": node.id,
        "tree_name": node.id_data.name,
        "node_name": node.name,
        "bl_idname": node.bl_idname,
    }


def _link_endpoint(node, socket):
    return {
        "node_name": node.name,
        "sn_id": getattr(node, "id", "") if is_sn(node) else None,
        "socket_name": socket.name,
    }


def _serialize_link(link):
    return {
        "from": _link_endpoint(link.from_node, link.from_socket),
        "to": _link_endpoint(link.to_node, link.to_socket),
        "is_muted": bool(getattr(link, "is_muted", False)),
    }


def _serialize_references(node):
    ref_props = getattr(node, "sn_reference_properties", {}) or {}
    if not ref_props:
        return {}
    settings = getattr(bpy.context.scene, "sna", None)
    out = {}
    for prop_name, allowed in ref_props.items():
        key = getattr(node, prop_name, "") or ""
        target = node.resolve_reference(prop_name) if key else None
        candidates = []
        if settings is not None:
            try:
                coll = getattr(settings, node._ref_collection_attr(prop_name))
            except (AttributeError, KeyError):
                coll = None
            if coll is not None:
                for entry in coll:
                    t = node_by_id(entry.node_id)
                    if t is not None:
                        candidates.append({"key": entry.name, **_node_ref(t)})
        out[prop_name] = {
            "current_key": key,
            "current_target": _node_ref(target) if target else None,
            "allowed_bl_idnames": list(allowed),
            "candidates": candidates,
        }
    return out


def _node_summary(node):
    # `dimensions` is only valid after first draw; width/height are settable.
    try:
        dims = [node.dimensions.x, node.dimensions.y]
    except (AttributeError, ReferenceError):
        dims = None
    summary = {
        "sn_id": node.id,
        "bl_idname": node.bl_idname,
        "name": node.name,
        "label": node.label,
        "location": [node.location.x, node.location.y],
        "width": node.width,
        "height": node.height,
        "dimensions": dims,
        "hide": bool(getattr(node, "hide", False)),
        "mute": node.mute,
        "inputs": [_serialize_socket(s) for s in node.inputs],
        "outputs": [_serialize_socket(s) for s in node.outputs],
        "props": _serialize_props(node),
    }
    refs = _serialize_references(node)
    if refs:
        summary["references"] = refs
    return summary


def _node_detail(node):
    detail = _node_summary(node)
    detail["code"] = {
        "imports": node.code_imports,
        "module": node.code_module,
        "inline": node.code_inline,
        "global": node.code_global,
        "register": node.code_register,
        "unregister": node.code_unregister,
    }
    return detail


# --- value coercion ---------------------------------------------------------


def _coerce_location(location, default=(0.0, 0.0)):
    if location is None:
        return default
    if not isinstance(location, (list, tuple)) or len(location) != 2:
        raise ValueError("location must be a 2-element [x, y] array")
    try:
        return (float(location[0]), float(location[1]))
    except (TypeError, ValueError):
        raise ValueError("location entries must be numbers")


def _coerce_prop_value(prop_def, value):
    if value is None:
        return None
    prop_type = prop_def.type
    if prop_type == "POINTER":
        if not isinstance(value, dict) or "name" not in value:
            raise ValueError(
                "PointerProperty values must be {'_ref': '<TypeName>', 'name': '<name>'}"
            )
        ref = value.get("_ref")
        if not ref:
            fixed = getattr(prop_def, "fixed_type", None)
            ref = getattr(fixed, "identifier", None) if fixed else None
        coll_attr = _BPY_DATA_COLLECTIONS.get(ref) if ref else None
        if coll_attr is None:
            raise ValueError(
                f"Don't know which bpy.data collection holds {ref!r}. "
                "Supported types: " + ", ".join(sorted(_BPY_DATA_COLLECTIONS))
            )
        coll = getattr(bpy.data, coll_attr, None)
        target = coll.get(value["name"]) if coll is not None else None
        if target is None:
            raise ValueError(
                f"No {ref} named {value['name']!r} in bpy.data.{coll_attr}"
            )
        return target
    if prop_type == "COLLECTION":
        raise ValueError("Setting CollectionProperty values is not supported")
    if getattr(prop_def, "is_array", False):
        if not isinstance(value, (list, tuple)):
            raise ValueError(
                f"{prop_type} array property requires a list, got {type(value).__name__}"
            )
        return list(value)
    # Some MCP transports stringify primitives when the schema doesn't pin a
    # type. Coerce so "true"/"1"/"1.5" land as bool/int/float.
    if isinstance(value, str):
        if prop_type == "BOOLEAN":
            low = value.strip().lower()
            if low in ("true", "1", "yes"):
                return True
            if low in ("false", "0", "no", ""):
                return False
            raise ValueError(f"Cannot coerce {value!r} to bool")
        if prop_type == "INT":
            try:
                return int(value)
            except ValueError:
                raise ValueError(f"Cannot coerce {value!r} to int")
        if prop_type == "FLOAT":
            try:
                return float(value)
            except ValueError:
                raise ValueError(f"Cannot coerce {value!r} to float")
    return value


def _coerce_blender_operator_value(value):
    # Picker stores "<label>  [<bl_idname>]"; accept bare bl_idnames and
    # translate so a direct "mesh.primitive_cube_add" doesn't silently become "".
    if not isinstance(value, str):
        raise ValueError("operator_blender expects a string")
    if not value:
        return ""
    if value.endswith("]") and "  [" in value:
        return value
    coll = getattr(bpy.context.window_manager, "sna_blender_operators", None)
    if coll is None:
        raise ValueError("Blender operator picker collection not populated yet")
    for entry in coll:
        if entry.bl_idname == value:
            return entry.name
    raise ValueError(
        f"No Blender operator with bl_idname {value!r}. Pass a known bl_idname "
        "or the full picker key '<label>  [<bl_idname>]'."
    )


def _coerce_reference_value(node, prop_name, value):
    settings = getattr(bpy.context.scene, "sna", None)
    coll = None
    if settings is not None:
        try:
            coll = getattr(settings, node._ref_collection_attr(prop_name))
        except (AttributeError, KeyError):
            coll = None
    if isinstance(value, dict):
        sn_id = value.get("sn_id")
        if not sn_id:
            raise ValueError(
                f"Reference property {prop_name!r} dict-form requires "
                "{'sn_id': '<target node id>'}"
            )
        if coll is None:
            raise ValueError(
                f"Signature collection for {prop_name!r} is unavailable"
            )
        for entry in coll:
            if entry.node_id == sn_id:
                return entry.name
        target = node_by_id(sn_id)
        if target is None:
            raise ValueError(f"No node with sn_id {sn_id!r}")
        raise ValueError(
            f"Target {target.bl_idname} ({sn_id}) is not a valid candidate "
            f"for {prop_name!r} on {node.bl_idname}"
        )
    if value == "" or value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(
            f"Reference property {prop_name!r} expects a string key or {{sn_id: '...'}} dict"
        )
    if coll is not None and not any(e.name == value for e in coll):
        raise ValueError(
            f"{value!r} is not a valid key for {prop_name!r}. "
            f"Available: {[e.name for e in coll]}"
        )
    return value


# --- tree update plumbing ---------------------------------------------------


# NodeTree.update only fires on UI-driven edits — call this after any
# Python-driven node/link mutation so SN's update_links → _generate
# propagation runs. The first call for a tree is snapshot-only (PREVIOUS_LINKS
# gate), so callers should also _generate() the affected endpoints explicitly.
def _drive_tree_update(ntree):
    ntree.update()


def _force_regen(*nodes):
    for n in nodes:
        if n is not None and hasattr(n, "_generate"):
            n._generate()


# --- read tools -------------------------------------------------------------


def list_node_trees():
    return {
        "trees": [
            {
                "name": ntree.name,
                "id": ntree.id,
                "module_name": ntree.module_name,
                "is_group": bool(ntree.is_group),
                "is_dirty": bool(ntree.is_dirty),
                "node_count": sum(1 for _ in sn_nodes(ntree)),
                "link_count": len(ntree.links),
            }
            for ntree in scripting_node_trees()
        ]
    }


def get_node_tree(tree_name: str):
    ntree = _find_tree(tree_name)
    return {
        "name": ntree.name,
        "id": ntree.id,
        "module_name": ntree.module_name,
        "is_group": bool(ntree.is_group),
        "is_dirty": bool(ntree.is_dirty),
        "nodes": [_node_summary(n) for n in sn_nodes(ntree)],
        "links": [_serialize_link(l) for l in ntree.links],
    }


def get_node(tree_name: str, node_id: str):
    ntree = _find_tree(tree_name)
    for node in sn_nodes(ntree):
        if node.id == node_id:
            return {"tree_name": tree_name, "node": _node_detail(node)}
    # Fallback: search all trees if caller doesn't know which one owns it.
    node = node_by_id(node_id)
    if node is not None:
        return {"tree_name": node.id_data.name, "node": _node_detail(node)}
    raise ValueError(f"No node with id {node_id!r} in tree {tree_name!r}")


def get_tree_code(tree_name: str):
    ntree = _find_tree(tree_name)
    return {
        "name": ntree.name,
        "module_name": ntree.module_name,
        "is_group": bool(ntree.is_group),
        "code": code_gen_node_tree(ntree),
    }


def get_addon_code():
    return {
        "trees": [
            {
                "name": ntree.name,
                "module_name": ntree.module_name,
                "is_group": bool(ntree.is_group),
                "code": code_gen_node_tree(ntree),
            }
            for ntree in scripting_node_trees()
        ]
    }


def list_node_types(category: str = None):
    items = []
    for cls in _iter_sn_node_classes():
        cat = _category_for_class(cls)
        if category and cat != category:
            continue
        items.append(
            {
                "bl_idname": cls.bl_idname,
                "bl_label": getattr(cls, "bl_label", ""),
                "category": cat,
            }
        )
    items.sort(key=lambda x: (x["category"], x["bl_label"], x["bl_idname"]))
    return {"node_types": items}


def get_node_type(bl_idname: str):
    target = next(
        (cls for cls in _iter_sn_node_classes() if cls.bl_idname == bl_idname),
        None,
    )
    if target is None:
        raise ValueError(f"No SN node class with bl_idname {bl_idname!r}")
    result = {
        "bl_idname": target.bl_idname,
        "bl_label": getattr(target, "bl_label", ""),
        "category": _category_for_class(target),
        "source_path": "",
        "source": "",
    }
    try:
        result["source"] = inspect.getsource(target)
    except (OSError, TypeError) as exc:
        result["note"] = f"Could not read source: {exc}"
    try:
        result["source_path"] = inspect.getsourcefile(target) or ""
    except TypeError:
        pass
    return result


def get_recent_logs(limit: int = 50):
    state = bpy.app.driver_namespace.get("_sn_log_overlay_state")
    if not state:
        return {"entries": [], "note": "log overlay buffer not yet initialized"}
    entries = list(state.get("entries") or [])
    if limit and limit > 0:
        entries = entries[-limit:]
    return {
        "entries": [
            {
                "level": e.level,
                "message": e.message,
                "timestamp": e.timestamp,
                "count": e.count,
            }
            for e in entries
        ]
    }


def resolve_node_reference(node_id: str, prop_name: str = None):
    node = _require_node(node_id)
    ref_props = getattr(node, "sn_reference_properties", {}) or {}
    keys = [prop_name] if prop_name is not None else list(ref_props.keys())
    return {
        "node": {"sn_id": node.id, "tree_name": node.id_data.name, "bl_idname": node.bl_idname},
        "references": [_resolve_one(node, k) for k in keys],
    }


def _resolve_one(node, prop_name):
    if prop_name not in node.sn_reference_properties:
        raise ValueError(f"{node.bl_idname} has no reference property {prop_name!r}")
    key = getattr(node, prop_name, "")
    if not key:
        return {"prop_name": prop_name, "key": "", "target": None}
    target = node.resolve_reference(prop_name)
    if target is None:
        return {
            "prop_name": prop_name,
            "key": key,
            "target": None,
            "note": "reference does not resolve to any node",
        }
    return {"prop_name": prop_name, "key": key, "target": _node_ref(target)}


# --- script content read / write -------------------------------------------


def _slice_lines(text, offset, limit):
    lines = text.splitlines()
    total = len(lines)
    offset = max(0, min(offset or 0, total))
    capped = min(limit or _READ_DEFAULT_LINES, _READ_MAX_LINES)
    end = min(total, offset + capped)
    sliced = "\n".join(lines[offset:end])
    returned = end - offset
    return sliced, total, returned, returned < (total - offset)


def read_script_content(
    node_id: str = None,
    text_name: str = None,
    offset: int = 0,
    limit: int = _READ_DEFAULT_LINES,
):
    if not node_id and not text_name:
        raise ValueError("Provide node_id (a Script node) or text_name")

    source = "internal"
    ref = None
    content = ""
    note = None

    if node_id:
        node = _require_node(node_id)
        if node.bl_idname != "SNA_Node_Script":
            raise ValueError(
                f"Node {node_id!r} is {node.bl_idname}, not SNA_Node_Script"
            )
        if getattr(node, "source_type", "INTERNAL") == "INTERNAL":
            tb = getattr(node, "text_block", None)
            if tb is None:
                note = "Script node has no text block assigned"
            else:
                ref = tb.name
                content = tb.as_string()
        else:
            source = "external"
            filepath = (getattr(node, "filepath", "") or "")
            ref = filepath
            if not filepath:
                note = "Script node has no filepath assigned"
            else:
                abspath = bpy.path.abspath(filepath)
                if not os.path.exists(abspath):
                    note = f"File not found: {abspath}"
                else:
                    try:
                        with open(abspath, "r", encoding="utf-8") as f:
                            content = f.read()
                    except Exception as exc:
                        note = f"Error reading file: {exc}"
    else:
        tb = bpy.data.texts.get(text_name)
        if tb is None:
            raise ValueError(f"No text block named {text_name!r}")
        ref = tb.name
        content = tb.as_string()

    sliced, total, returned, truncated = _slice_lines(content, offset, limit)
    result = {
        "source": source,
        "ref": ref,
        "total_lines": total,
        "offset": max(0, offset or 0),
        "lines_returned": returned,
        "truncated": truncated,
        "content": sliced,
    }
    if note:
        result["note"] = note
    return result


def _resolve_script_target(node_id, text_name):
    # Returns (kind, text_block, abs_filepath, ref_for_response). Raises if
    # not exactly one of (node_id, text_name) is supplied or the target is
    # missing — used by writes which need a definite target.
    if (node_id is None) == (text_name is None):
        raise ValueError("Provide exactly one of node_id or text_name")
    if node_id:
        node = _require_node(node_id)
        if node.bl_idname != "SNA_Node_Script":
            raise ValueError(
                f"Node {node_id!r} is {node.bl_idname}, not SNA_Node_Script"
            )
        if getattr(node, "source_type", "INTERNAL") == "INTERNAL":
            tb = node.text_block
            if tb is None:
                raise ValueError("Script node has no text block assigned")
            return "text_block", tb, None, tb.name
        filepath = (node.filepath or "").strip()
        if not filepath:
            raise ValueError("Script node has no filepath assigned")
        abspath = bpy.path.abspath(filepath)
        return "file", None, abspath, abspath
    tb = bpy.data.texts.get(text_name)
    if tb is None:
        raise ValueError(f"No text block named {text_name!r}")
    return "text_block", tb, None, tb.name


def _read_current(target_kind, text_block, abs_filepath):
    if target_kind == "text_block":
        return text_block.as_string()
    try:
        with open(abs_filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""
    except OSError as exc:
        raise ValueError(f"Could not read {abs_filepath}: {exc}")


def _apply_replace(current, replace):
    # Edit-tool semantics: unique match required unless replace_all.
    if not isinstance(replace, dict):
        raise ValueError("replace must be an object with 'old' and 'new'")
    old = replace.get("old")
    new = replace.get("new")
    if not isinstance(old, str) or not isinstance(new, str):
        raise ValueError("replace.old and replace.new must both be strings")
    if not old:
        raise ValueError("replace.old must not be empty")
    replace_all = bool(replace.get("replace_all", False))
    count = current.count(old)
    if count == 0:
        raise ValueError("replace.old was not found in the current content")
    if count > 1 and not replace_all:
        raise ValueError(
            f"replace.old appears {count} times — add surrounding context "
            "to make it unique, or set replace.replace_all=true"
        )
    if replace_all:
        return current.replace(old, new), count
    return current.replace(old, new, 1), 1


def _regenerate_dependents(target_kind, text_block, abs_filepath):
    # Refresh every Script node pointing at the modified target so its
    # embedded code stays in sync.
    norm_target = os.path.normpath(abs_filepath) if target_kind == "file" else None
    touched = []
    for ntree in scripting_node_trees():
        for sn in sn_nodes(ntree):
            if sn.bl_idname != "SNA_Node_Script":
                continue
            stype = getattr(sn, "source_type", "INTERNAL")
            matches = False
            if target_kind == "text_block" and stype == "INTERNAL":
                matches = sn.text_block is text_block
            elif target_kind == "file" and stype == "EXTERNAL":
                p = (sn.filepath or "").strip()
                if p:
                    matches = os.path.normpath(bpy.path.abspath(p)) == norm_target
            if matches:
                sn._generate()
                touched.append(
                    {
                        "tree_name": ntree.name,
                        "sn_id": sn.id,
                        "node_name": sn.name,
                    }
                )
    return touched


def write_script_content(
    node_id: str = None,
    text_name: str = None,
    content: str = None,
    replace: dict = None,
):
    if (content is None) == (replace is None):
        raise ValueError("Provide exactly one of content or replace")

    kind, text_block, abs_filepath, ref = _resolve_script_target(node_id, text_name)

    if content is not None:
        new_content = content
        replacements = None
    else:
        current = _read_current(kind, text_block, abs_filepath)
        new_content, replacements = _apply_replace(current, replace)

    if kind == "text_block":
        text_block.clear()
        text_block.write(new_content)
    else:
        parent = os.path.dirname(abs_filepath)
        if parent:
            os.makedirs(parent, exist_ok=True)
        try:
            with open(abs_filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
        except OSError as exc:
            raise ValueError(f"Could not write {abs_filepath}: {exc}")

    return {
        "target_kind": kind,
        "ref": ref,
        "bytes_written": len(new_content.encode("utf-8")),
        "mode": "replace" if replace is not None else "content",
        "replacements_made": replacements,
        "regenerated_script_nodes": _regenerate_dependents(
            kind, text_block, abs_filepath
        ),
    }


# --- structural write tools -------------------------------------------------


def create_node(
    tree_name: str,
    bl_idname: str,
    location=None,
    socket_values: dict = None,
):
    ntree = _find_tree(tree_name)
    if bl_idname not in {cls.bl_idname for cls in _iter_sn_node_classes()}:
        raise ValueError(
            f"Unknown SN node bl_idname: {bl_idname!r}. Use list_node_types "
            "to see what's available."
        )
    try:
        node = ntree.nodes.new(bl_idname)
    except RuntimeError as exc:
        raise ValueError(f"Blender refused to create {bl_idname}: {exc}")
    node.location = _coerce_location(location)
    if socket_values:
        if not isinstance(socket_values, dict):
            raise ValueError("socket_values must be an object {name: value}")
        for sock_name, raw in socket_values.items():
            sock = _socket_by_name(node, "input", sock_name)
            if "value" not in sock.bl_rna.properties:
                raise ValueError(
                    f"Input socket {sock_name!r} ({sock.bl_idname}) has no settable `value`"
                )
            sock.value = _coerce_prop_value(
                sock.bl_rna.properties["value"], raw
            )
    return {"tree_name": ntree.name, "node": _node_summary(node)}


def delete_node(tree_name: str, node_id: str):
    ntree = _find_tree(tree_name)
    target = next(
        (n for n in ntree.nodes if getattr(n, "id", "") == node_id), None
    )
    if target is None:
        raise ValueError(f"No node with id {node_id!r} in tree {tree_name!r}")
    info = {"sn_id": node_id, "name": target.name, "bl_idname": target.bl_idname}
    ntree.nodes.remove(target)
    _drive_tree_update(ntree)
    return {"tree_name": tree_name, "deleted": info}


def move_node(node_id: str, location):
    node = _require_node(node_id)
    coords = _coerce_location(location, default=None)
    if coords is None:
        raise ValueError("location is required")
    node.location = coords
    return {
        "sn_id": node_id,
        "tree_name": node.id_data.name,
        "location": [node.location.x, node.location.y],
    }


def _set_socket_attr(node, head, rest, value):
    socket_name, _, sub = rest.partition(".")
    sub_attr = sub or "value"
    kind = "input" if head == "inputs" else "output"
    socket = _socket_by_name(node, kind, socket_name)
    if sub_attr not in socket.bl_rna.properties:
        raise ValueError(
            f"Socket {head}.{socket_name} ({socket.bl_idname}) has no property {sub_attr!r}"
        )
    sock_def = socket.bl_rna.properties[sub_attr]
    if sock_def.is_readonly:
        raise ValueError(
            f"Socket property {sub_attr!r} on {head}.{socket_name} is read-only"
        )
    try:
        setattr(socket, sub_attr, _coerce_prop_value(sock_def, value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Could not set {head}.{socket_name}.{sub_attr}: {exc}")
    return socket, sub_attr


def set_node_prop(node_id: str, prop_name: str, value):
    node = _require_node(node_id)

    # 'inputs.<name>[.<attr>]' / 'outputs.<name>[.<attr>]' targets a socket
    # field; default attr is `value` (the unlinked DATA literal).
    if "." in prop_name:
        head, _, rest = prop_name.partition(".")
        if head in ("inputs", "outputs"):
            socket, sub_attr = _set_socket_attr(node, head, rest, value)
            return {
                "sn_id": node_id,
                "tree_name": node.id_data.name,
                "prop_name": prop_name,
                "value": _serialize_value(getattr(socket, sub_attr)),
            }

    if prop_name not in node.bl_rna.properties:
        raise ValueError(
            f"{node.bl_idname} has no property {prop_name!r}. "
            "Use get_node or get_node_type to see available props. "
            "Socket literals are addressed as 'inputs.<name>'."
        )
    prop_def = node.bl_rna.properties[prop_name]
    if prop_def.is_readonly:
        raise ValueError(f"Property {prop_name!r} is read-only")
    ref_props = getattr(node, "sn_reference_properties", {}) or {}
    if prop_name in ref_props:
        coerced = _coerce_reference_value(node, prop_name, value)
    elif prop_name == "operator_blender":
        coerced = _coerce_blender_operator_value(value)
    else:
        coerced = _coerce_prop_value(prop_def, value)
    try:
        setattr(node, prop_name, coerced)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Could not set {prop_name}: {exc}")
    return {
        "sn_id": node_id,
        "tree_name": node.id_data.name,
        "prop_name": prop_name,
        "value": _serialize_value(getattr(node, prop_name)),
    }


def connect_sockets(
    from_node_id: str,
    from_socket: str,
    to_node_id: str,
    to_socket: str,
):
    src_node, src, dst_node, dst, ntree = _resolve_link_endpoints(
        from_node_id, from_socket, to_node_id, to_socket
    )
    link = ntree.links.new(src, dst)
    _drive_tree_update(ntree)
    _force_regen(src_node, dst_node)
    return {
        "tree_name": ntree.name,
        "from": {"sn_id": from_node_id, "socket_name": from_socket},
        "to": {"sn_id": to_node_id, "socket_name": to_socket},
        "is_muted": bool(getattr(link, "is_muted", False)),
    }


def disconnect_sockets(
    from_node_id: str,
    from_socket: str,
    to_node_id: str,
    to_socket: str,
):
    src_node, src, dst_node, dst, ntree = _resolve_link_endpoints(
        from_node_id, from_socket, to_node_id, to_socket
    )
    target = next(
        (l for l in ntree.links if l.from_socket is src and l.to_socket is dst),
        None,
    )
    if target is None:
        raise ValueError(
            f"No link between {src_node.name!r}.{from_socket} and "
            f"{dst_node.name!r}.{to_socket}"
        )
    ntree.links.remove(target)
    _drive_tree_update(ntree)
    _force_regen(src_node, dst_node)
    return {
        "tree_name": ntree.name,
        "removed": {
            "from": {"sn_id": from_node_id, "socket_name": from_socket},
            "to": {"sn_id": to_node_id, "socket_name": to_socket},
        },
    }


# --- tool registry (descriptions are LLM-facing; keep verbose) -------------


TOOLS = {
    "list_node_trees": {
        "fn": list_node_trees,
        "description": (
            "List all Scripting Nodes node trees in the current blend with "
            "per-tree counts and dirty state."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    "get_node_tree": {
        "fn": get_node_tree,
        "description": (
            "Return a structural snapshot of one node tree: every Scripting "
            "Nodes node with its props/sockets, plus all links."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "tree_name": {
                    "type": "string",
                    "description": "Name of the node tree (as shown in the editor).",
                }
            },
            "required": ["tree_name"],
            "additionalProperties": False,
        },
    },
    "get_node": {
        "fn": get_node,
        "description": (
            "Return full details for one node, including its generated code "
            "fragments (imports/module/inline/global/register/unregister)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "tree_name": {
                    "type": "string",
                    "description": (
                        "Tree the node is expected to live in. If the id is "
                        "not found there, all trees are searched as a fallback."
                    ),
                },
                "node_id": {
                    "type": "string",
                    "description": "The node's Scripting Nodes UUID (its `sn_id`).",
                },
            },
            "required": ["tree_name", "node_id"],
            "additionalProperties": False,
        },
    },
    "get_tree_code": {
        "fn": get_tree_code,
        "description": (
            "Compile one node tree to Python and return the generated module "
            "source — what the codegen would write to disk."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "tree_name": {"type": "string"},
            },
            "required": ["tree_name"],
            "additionalProperties": False,
        },
    },
    "get_addon_code": {
        "fn": get_addon_code,
        "description": (
            "Compile every node tree in the blend and return all generated "
            "module sources in one payload."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    "read_script_content": {
        "fn": read_script_content,
        "description": (
            "Read the script source referenced by a Script node (internal text "
            "block or external file), or any text block by name. Returns at "
            f"most {_READ_MAX_LINES} lines per call (default {_READ_DEFAULT_LINES}); "
            "page with offset+limit for larger files."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "node_id": {
                    "type": "string",
                    "description": (
                        "Scripting Nodes UUID of a Script node — its "
                        "configured source (internal text block or external "
                        "filepath) is read."
                    ),
                },
                "text_name": {
                    "type": "string",
                    "description": (
                        "Name of a bpy.data.texts block to read directly. "
                        "Provide this OR node_id."
                    ),
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "First line to return (0-indexed). Default 0.",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": _READ_MAX_LINES,
                    "description": (
                        f"Max lines to return. Default {_READ_DEFAULT_LINES}, "
                        f"hard cap {_READ_MAX_LINES}."
                    ),
                },
            },
            "additionalProperties": False,
        },
    },
    "resolve_node_reference": {
        "fn": resolve_node_reference,
        "description": (
            "Resolve a node's `sn_reference_properties` (e.g. Get/Set Variable "
            "pointing at a Variable node) to the target node — works "
            "cross-tree. Omit prop_name to resolve every reference on the node."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "node_id": {
                    "type": "string",
                    "description": "Scripting Nodes UUID of the referencing node.",
                },
                "prop_name": {
                    "type": "string",
                    "description": (
                        "Specific reference property to resolve. Omit to "
                        "resolve all reference properties declared on the node."
                    ),
                },
            },
            "required": ["node_id"],
            "additionalProperties": False,
        },
    },
    "write_script_content": {
        "fn": write_script_content,
        "description": (
            "Write the script source referenced by a Script node (internal "
            "text block or external file) or any text block by name. Use "
            "`content` for a full replacement, or `replace` for an in-place "
            "edit. After a successful write every Script node referencing "
            "the modified target is re-generated so its embedded code stays "
            "in sync."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "node_id": {
                    "type": "string",
                    "description": (
                        "Scripting Nodes UUID of a Script node — writes to "
                        "its configured source (text block or filepath)."
                    ),
                },
                "text_name": {
                    "type": "string",
                    "description": (
                        "Name of a bpy.data.texts block to write directly. "
                        "Provide this OR node_id."
                    ),
                },
                "content": {
                    "type": "string",
                    "description": "Full replacement content for the target.",
                },
                "replace": {
                    "type": "object",
                    "description": (
                        "In-place edit. `old` must appear in the current "
                        "content; by default it must be unique unless "
                        "replace_all is true."
                    ),
                    "properties": {
                        "old": {
                            "type": "string",
                            "description": "Exact substring to replace.",
                        },
                        "new": {
                            "type": "string",
                            "description": "Replacement text.",
                        },
                        "replace_all": {
                            "type": "boolean",
                            "description": (
                                "Replace every occurrence of `old`. Default "
                                "false: errors if `old` is not unique."
                            ),
                        },
                    },
                    "required": ["old", "new"],
                    "additionalProperties": False,
                },
            },
            "additionalProperties": False,
        },
    },
    "create_node": {
        "fn": create_node,
        "description": (
            "Add a new node to an existing Scripting Nodes tree. Returns the "
            "new node's full summary including the freshly-assigned sn_id "
            "you'll need for follow-up calls (set_node_prop, connect_sockets). "
            "Use `socket_values` to seed input-socket literals (Label, Align, "
            "defaults, …) in the same call instead of N follow-up writes. "
            "IMPORTANT: when building an interface chain, connect the chain "
            "BEFORE setting non-socket props on layout-aware nodes (Button, "
            "VectorField, etc.) — their generate() reads the parent layout "
            "var from the linked input at call time; configuring an "
            "orphaned node bakes self.layout into its cached code."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "tree_name": {"type": "string"},
                "bl_idname": {
                    "type": "string",
                    "description": (
                        "Node class to instantiate. Use list_node_types to "
                        "discover what's available."
                    ),
                },
                "location": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 2,
                    "maxItems": 2,
                    "description": (
                        "[x, y] in node-editor units. Defaults to [0, 0]."
                    ),
                },
                "socket_values": {
                    "type": "object",
                    "description": (
                        "Optional {input socket name: literal} dict. Sets "
                        "each named input's `value` (the unlinked-literal "
                        "field every DATA socket exposes)."
                    ),
                    "additionalProperties": True,
                },
            },
            "required": ["tree_name", "bl_idname"],
            "additionalProperties": False,
        },
    },
    "delete_node": {
        "fn": delete_node,
        "description": "Remove a node from a tree by its sn_id.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tree_name": {"type": "string"},
                "node_id": {"type": "string"},
            },
            "required": ["tree_name", "node_id"],
            "additionalProperties": False,
        },
    },
    "move_node": {
        "fn": move_node,
        "description": (
            "Reposition a node. Use this to lay graphs out cleanly — read the "
            "tree first to learn each node's width/height/dimensions and "
            "pack new nodes without overlap."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "node_id": {"type": "string"},
                "location": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 2,
                    "maxItems": 2,
                },
            },
            "required": ["node_id", "location"],
            "additionalProperties": False,
        },
    },
    "set_node_prop": {
        "fn": set_node_prop,
        "description": (
            "Set one property on a node. Three common forms: "
            "(1) Node prop — prop_name='emboss', value=true/1/'hello'. "
            "Strings are coerced to BOOL/INT/FLOAT based on the destination "
            "type. "
            "(2) Socket literal — prop_name='inputs.<socket name>' writes "
            "the socket's `value` field (the literal emitted when the input "
            "is unlinked). This is how you supply a string/number/bool to a "
            "node without wiring a constant-value node. "
            "(3) Special prop forms: PointerProperty values use {_ref: "
            "'<TypeName>', name: '<name>'} (same shape get_node emits); "
            "reference props (those listed under `references` in get_node) "
            "additionally accept {sn_id: '<target node id>'}; "
            "`operator_blender` accepts a bare bl_idname like "
            "'mesh.primitive_cube_add' (translated to the picker's display "
            "format)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "node_id": {"type": "string"},
                "prop_name": {"type": "string"},
                "value": {
                    "description": (
                        "New value. Type depends on the property: string/int/"
                        "float/bool/enum-string, [x,y,z]-style array for "
                        "vectors, {_ref, name} for pointers."
                    ),
                },
            },
            "required": ["node_id", "prop_name", "value"],
            "additionalProperties": False,
        },
    },
    "connect_sockets": {
        "fn": connect_sockets,
        "description": (
            "Create a link from one node's output socket to another node's "
            "input socket. Sockets are addressed by name (case-sensitive) — "
            "see `get_node` for available names. Type mismatches (PROGRAM vs "
            "DATA) auto-mute; check the result's is_muted."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "from_node_id": {"type": "string"},
                "from_socket": {
                    "type": "string",
                    "description": "Output socket name on the source node.",
                },
                "to_node_id": {"type": "string"},
                "to_socket": {
                    "type": "string",
                    "description": "Input socket name on the target node.",
                },
            },
            "required": [
                "from_node_id",
                "from_socket",
                "to_node_id",
                "to_socket",
            ],
            "additionalProperties": False,
        },
    },
    "disconnect_sockets": {
        "fn": disconnect_sockets,
        "description": (
            "Remove the existing link between two specific sockets. Errors "
            "if there is no link between them."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "from_node_id": {"type": "string"},
                "from_socket": {"type": "string"},
                "to_node_id": {"type": "string"},
                "to_socket": {"type": "string"},
            },
            "required": [
                "from_node_id",
                "from_socket",
                "to_node_id",
                "to_socket",
            ],
            "additionalProperties": False,
        },
    },
    "list_node_types": {
        "fn": list_node_types,
        "description": (
            "Catalog every Scripting Nodes node type — bl_idname, label, and "
            "category. Use this to discover what nodes exist before deciding "
            "what to wire up."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": (
                        "Optional category filter (e.g. 'Interface', 'Logic', "
                        "'Program', 'Data', 'Events', 'Math', 'Variables', "
                        "'Properties', 'Groups')."
                    ),
                },
            },
            "additionalProperties": False,
        },
    },
    "get_node_type": {
        "fn": get_node_type,
        "description": (
            "Return the full Python source of a node class — its on_create "
            "(sockets), annotations (props), draw (UI), and generate (what "
            "Python the node compiles to). Reading the source is the "
            "authoritative way to understand what a node does."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "bl_idname": {
                    "type": "string",
                    "description": "The node class's bl_idname (e.g. 'SNA_Node_Panel').",
                },
            },
            "required": ["bl_idname"],
            "additionalProperties": False,
        },
    },
    "get_recent_logs": {
        "fn": get_recent_logs,
        "description": (
            "Recent SN log entries (level/message/timestamp/count) from the "
            "in-Blender log overlay buffer. Captures codegen errors, reload "
            "events, and anything routed through the SN logger — but not raw "
            "stderr from the generated addon's own classes."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Max entries to return (newest last). Default 50.",
                },
            },
            "additionalProperties": False,
        },
    },
}
