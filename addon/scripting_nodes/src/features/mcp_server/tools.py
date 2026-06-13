"""MCP tool definitions for Scripting Nodes.

Every tool runs on Blender's main thread (the server module hands them off
via `bridge.call_on_main`). Tool functions touch bpy directly and return
plain JSON-serializable dicts / lists.
"""

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


# Hard upper bound for any single read_script_content call — even if a caller
# asks for more, we never return more than this so a multi-MB script can't
# blow up an MCP response in one shot.
_READ_MAX_LINES = 300
_READ_DEFAULT_LINES = 100


# Code/id fields declared on ScriptingBaseNode — surfacing them in `props`
# would just be noise (the `code` block of get_node already exposes them).
_INTERNAL_PROPS = {
    "id",
    "code_imports",
    "code_module",
    "code_inline",
    "code_global",
    "code_register",
    "code_unregister",
}


def _sn_prop_names(node):
    """SN-declared bpy properties on a node class, in declaration order, with
    base-node code/id fields filtered out.

    Walks MRO from the concrete class up to and including ScriptingBaseNode,
    so it catches both per-node fields (e.g. `variables_json` on Script) and
    the few bpy props declared on the base (`id`, `code_*`) — those get
    filtered by _INTERNAL_PROPS. PEP 526 type-only annotations like
    `sn_options: Set[...] = {}` are skipped via the _PropertyDeferred check;
    they're class-level metadata, not bpy data.
    """
    names = []
    seen = set(_INTERNAL_PROPS)
    for cls in type(node).__mro__:
        anns = cls.__dict__.get("__annotations__", {}) or {}
        for k, v in anns.items():
            if k in seen:
                continue
            if not isinstance(v, bpy.props._PropertyDeferred):
                continue
            seen.add(k)
            names.append(k)
        if cls is ScriptingBaseNode:
            break
    return names


def _serialize_value(val):
    """Best-effort JSON-safe conversion of a bpy property value."""
    if val is None or isinstance(val, (bool, int, float, str)):
        return val
    # bpy ID datablock reference (Text, Image, Object, NodeTree, ...): emit
    # a typed name-ref so the client can re-resolve it without exposing
    # the live pointer.
    if isinstance(val, bpy.types.ID):
        return {"_ref": type(val).__name__, "name": val.name}
    # Vector / Euler / Color / array-like — fall through to list conversion.
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
    label = getattr(socket, "label", "")
    if label:
        info["label"] = label
    socket_type = getattr(socket, "socket_type", None)
    if socket_type is not None:
        info["socket_type"] = socket_type
    return info


def _node_identity(node):
    """Stable (name, sn_id) pair for a node — sn_id is None for non-SN nodes
    like NodeReroute. Clients should prefer sn_id when present; fall back to
    name (unique within a tree) otherwise.
    """
    return {
        "node_name": node.name,
        "sn_id": getattr(node, "id", "") if is_sn(node) else None,
    }


def _serialize_link(link):
    return {
        "from": {
            **_node_identity(link.from_node),
            "socket_name": link.from_socket.name,
        },
        "to": {
            **_node_identity(link.to_node),
            "socket_name": link.to_socket.name,
        },
        "is_muted": bool(getattr(link, "is_muted", False)),
    }


def _node_summary(node):
    summary = {
        "sn_id": node.id,
        "bl_idname": node.bl_idname,
        "name": node.name,
        "label": node.label,
        "location": [node.location.x, node.location.y],
        "width": node.width,
        "mute": node.mute,
        "inputs": [_serialize_socket(s) for s in node.inputs],
        "outputs": [_serialize_socket(s) for s in node.outputs],
        "props": _serialize_props(node),
    }
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


def _find_tree(name):
    ntree = bpy.data.node_groups.get(name)
    if ntree is None or not is_sn(ntree):
        raise ValueError(f"No scripting node tree named {name!r}")
    return ntree


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


def list_node_trees():
    trees = []
    for ntree in scripting_node_trees():
        trees.append(
            {
                "name": ntree.name,
                "id": ntree.id,
                "module_name": ntree.module_name,
                "is_group": bool(ntree.is_group),
                "is_dirty": bool(ntree.is_dirty),
                "node_count": sum(1 for _ in sn_nodes(ntree)),
                "link_count": len(ntree.links),
            }
        )
    return {"trees": trees}


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
    # Fall back to scanning all trees — useful when the caller doesn't know
    # which tree a node id lives in.
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
    trees = []
    for ntree in scripting_node_trees():
        trees.append(
            {
                "name": ntree.name,
                "module_name": ntree.module_name,
                "is_group": bool(ntree.is_group),
                "code": code_gen_node_tree(ntree),
            }
        )
    return {"trees": trees}


# ---------------------------------------------------------------------------
# Debugging helpers — read script content, resolve references, recent logs.
# ---------------------------------------------------------------------------


def _slice_lines(text: str, offset: int, limit: int):
    """Return (sliced_text, total_lines, lines_returned, truncated) — slice
    the text by offset/limit, clamp limit to _READ_MAX_LINES, never raise
    on negative or out-of-range offsets (clamp to [0, total]).
    """
    lines = text.splitlines()
    total = len(lines)
    if offset is None or offset < 0:
        offset = 0
    if offset > total:
        offset = total
    if limit is None or limit <= 0:
        limit = _READ_DEFAULT_LINES
    capped = min(limit, _READ_MAX_LINES)
    end = min(total, offset + capped)
    sliced = "\n".join(lines[offset:end])
    returned = end - offset
    truncated = returned < (total - offset)
    return sliced, total, returned, truncated


def read_script_content(
    node_id: str = None,
    text_name: str = None,
    offset: int = 0,
    limit: int = _READ_DEFAULT_LINES,
):
    """Read the script content referenced by a Script node, or any text block
    by name. Returns at most _READ_MAX_LINES regardless of `limit` so a
    rogue megabyte file can't overflow one response.
    """
    if not node_id and not text_name:
        raise ValueError("Provide node_id (a Script node) or text_name")

    source = None
    ref = None
    content = ""
    note = None

    if node_id:
        node = node_by_id(node_id)
        if node is None:
            raise ValueError(f"No node with id {node_id!r}")
        if node.bl_idname != "SNA_Node_Script":
            raise ValueError(
                f"Node {node_id!r} is {node.bl_idname}, not SNA_Node_Script"
            )
        source_type = getattr(node, "source_type", "INTERNAL")
        if source_type == "INTERNAL":
            source = "internal"
            text_block = getattr(node, "text_block", None)
            if text_block is None:
                note = "Script node has no text block assigned"
            else:
                ref = text_block.name
                content = text_block.as_string()
        else:
            source = "external"
            filepath = getattr(node, "filepath", "") or ""
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
        source = "internal"
        text_block = bpy.data.texts.get(text_name)
        if text_block is None:
            raise ValueError(f"No text block named {text_name!r}")
        ref = text_block.name
        content = text_block.as_string()

    sliced, total, returned, truncated = _slice_lines(content, offset, limit)
    result = {
        "source": source,
        "ref": ref,
        "total_lines": total,
        "offset": offset if offset and offset > 0 else 0,
        "lines_returned": returned,
        "truncated": truncated,
        "content": sliced,
    }
    if note:
        result["note"] = note
    return result


def _resolve_one(node, prop_name):
    """Return [{target: {...}}] for a single sn_reference_property entry. If
    the node defines `prop_name` but doesn't actually reference anything,
    returns the entry with target=None so callers see "looked up, empty".
    """
    if prop_name not in node.sn_reference_properties:
        raise ValueError(
            f"{node.bl_idname} has no reference property {prop_name!r}"
        )
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
    return {
        "prop_name": prop_name,
        "key": key,
        "target": {
            "tree_name": target.id_data.name,
            "sn_id": target.id,
            "bl_idname": target.bl_idname,
            "node_name": target.name,
        },
    }


def resolve_node_reference(node_id: str, prop_name: str = None):
    """Resolve one or all `sn_reference_properties` on a node to their target
    nodes. Cross-tree refs (e.g. Get Variable pointing at a Variable in
    another tree) resolve too — `target.tree_name` tells you where it lives.
    """
    node = node_by_id(node_id)
    if node is None:
        raise ValueError(f"No node with id {node_id!r}")
    ref_props = getattr(node, "sn_reference_properties", {}) or {}
    if prop_name is not None:
        return {
            "node": {
                "sn_id": node.id,
                "tree_name": node.id_data.name,
                "bl_idname": node.bl_idname,
            },
            "references": [_resolve_one(node, prop_name)],
        }
    return {
        "node": {
            "sn_id": node.id,
            "tree_name": node.id_data.name,
            "bl_idname": node.bl_idname,
        },
        "references": [_resolve_one(node, p) for p in ref_props.keys()],
    }


def _resolve_script_target(node_id, text_name):
    """Return ('text_block' | 'file', text_block_or_None, abs_filepath_or_None, ref_for_response).

    Validates that exactly one of node_id / text_name is provided and the
    referenced target actually exists / is configured.
    """
    if (node_id is None) == (text_name is None):
        raise ValueError("Provide exactly one of node_id or text_name")
    if node_id:
        node = node_by_id(node_id)
        if node is None:
            raise ValueError(f"No node with id {node_id!r}")
        if node.bl_idname != "SNA_Node_Script":
            raise ValueError(
                f"Node {node_id!r} is {node.bl_idname}, not SNA_Node_Script"
            )
        source_type = getattr(node, "source_type", "INTERNAL")
        if source_type == "INTERNAL":
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
        # OK — write_script_content can create the file. Read returns empty so
        # `replace` mode against a missing file fails on "old not found", which
        # is the right error.
        return ""
    except OSError as exc:
        raise ValueError(f"Could not read {abs_filepath}: {exc}")


def _apply_replace(current, replace):
    """Compute (new_content, replacements_count) from a replace directive.
    Mirrors Edit tool semantics: unique-match required unless replace_all.
    """
    if not isinstance(replace, dict):
        raise ValueError("replace must be an object with 'old' and 'new'")
    old = replace.get("old")
    new = replace.get("new")
    if not isinstance(old, str) or not isinstance(new, str):
        raise ValueError("replace.old and replace.new must both be strings")
    if old == "":
        raise ValueError("replace.old must not be empty")
    replace_all = bool(replace.get("replace_all", False))
    count = current.count(old)
    if count == 0:
        raise ValueError("replace.old was not found in the current content")
    if count > 1 and not replace_all:
        raise ValueError(
            f"replace.old appears {count} times — add surrounding context to "
            "make it unique, or set replace.replace_all=true"
        )
    if replace_all:
        return current.replace(old, new), count
    return current.replace(old, new, 1), 1


def _regenerate_dependents(target_kind, text_block, abs_filepath):
    """Re-run generate() on every Script node pointing at the modified target,
    so its `code_inline` re-embeds the new content and dirties its tree.
    Returns the list of nodes touched.
    """
    touched = []
    norm_target = (
        os.path.normpath(abs_filepath) if target_kind == "file" else None
    )
    for ntree in scripting_node_trees():
        for sn in sn_nodes(ntree):
            if sn.bl_idname != "SNA_Node_Script":
                continue
            source_type = getattr(sn, "source_type", "INTERNAL")
            matches = False
            if target_kind == "text_block" and source_type == "INTERNAL":
                matches = sn.text_block is text_block
            elif target_kind == "file" and source_type == "EXTERNAL":
                sn_path = (sn.filepath or "").strip()
                if sn_path:
                    matches = (
                        os.path.normpath(bpy.path.abspath(sn_path)) == norm_target
                    )
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
    """Write the script source referenced by a Script node (internal text
    block or external file), or any text block by name.

    Provide either `content` (full replacement) or `replace` (in-place edit).
    After a successful write, every Script node referencing the modified
    target is re-run through `generate()` so its embedded code stays in sync.
    """
    if (content is None) == (replace is None):
        raise ValueError("Provide exactly one of content or replace")

    target_kind, text_block, abs_filepath, ref = _resolve_script_target(
        node_id, text_name
    )

    if content is not None:
        new_content = content
        replacements = None
    else:
        current = _read_current(target_kind, text_block, abs_filepath)
        new_content, replacements = _apply_replace(current, replace)

    if target_kind == "text_block":
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

    regenerated = _regenerate_dependents(target_kind, text_block, abs_filepath)

    return {
        "target_kind": target_kind,
        "ref": ref,
        "bytes_written": len(new_content.encode("utf-8")),
        "mode": "replace" if replace is not None else "content",
        "replacements_made": replacements,
        "regenerated_script_nodes": regenerated,
    }


def get_recent_logs(limit: int = 50):
    """Recent SN log entries from the in-Blender log overlay buffer.

    Source is the same deque the on-screen overlay reads, so anything routed
    through `lib.utils.logger.log()` is here — codegen errors, reload
    events, dependency-tracker warnings. Plain `print()` from generated
    addon code is NOT captured; if that turns out to be the gap, we'd
    install a stderr tee at server-start time.
    """
    state = bpy.app.driver_namespace.get("_sn_log_overlay_state")
    if not state:
        return {"entries": [], "note": "log overlay buffer not yet initialized"}
    entries = list(state.get("entries") or [])
    if limit and limit > 0:
        entries = entries[-limit:]
    out = []
    for entry in entries:
        out.append(
            {
                "level": entry.level,
                "message": entry.message,
                "timestamp": entry.timestamp,
                "count": entry.count,
            }
        )
    return {"entries": out}


# ---------------------------------------------------------------------------
# Tool registry — used by the JSON-RPC handler to expose tools/list and route
# tools/call. Each entry is (callable, JSON-Schema input).
# ---------------------------------------------------------------------------


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
