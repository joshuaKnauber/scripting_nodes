"""Scripts: text blocks and files used by Script nodes."""

import os

import bpy

from ...lib.trees import scripting_node_trees, sn_nodes
from . import tool
from ._common import ToolError, find_node

_LIMIT = 400


def _target(node="", text="", file=""):
    """("text", block) or ("file", path) of what to read / write."""
    if sum(bool(x) for x in (node, text, file)) != 1:
        raise ToolError("Give one of node (a Script node), text or file")
    if node:
        script = find_node(node)
        if script.bl_idname != "SNA_Node_Script":
            raise ToolError(f"{script.name!r} isn't a Script node")
        if script.source_type == "INTERNAL":
            if script.text_block is None:
                raise ToolError("The Script node has no text block: pick one")
            return "text", script.text_block
        if not script.filepath:
            raise ToolError("The Script node has no file: set its filepath")
        return "file", bpy.path.abspath(script.filepath)
    if text:
        return "text", text
    return "file", os.path.abspath(bpy.path.abspath(file))


@tool(
    "read_text",
    """Read a script: the text of a Script node, a text block by name or a
    file. Long texts come in pages of lines (offset, limit).""",
    {
        "node": {"type": "string"},
        "text": {"type": "string"},
        "file": {"type": "string"},
        "offset": {"type": "integer"},
        "limit": {"type": "integer"},
    },
)
def read_text(node="", text="", file="", offset=0, limit=_LIMIT):
    kind, target = _target(node, text, file)
    if kind == "text":
        block = (
            target if isinstance(target, bpy.types.Text) else bpy.data.texts.get(target)
        )
        if block is None:
            raise ToolError(
                f"No text block {target!r}. Texts: {list(bpy.data.texts.keys())}"
            )
        content, name = block.as_string(), block.name
    else:
        if not os.path.exists(target):
            raise ToolError(f"No file {target}")
        with open(target, encoding="utf-8") as f:
            content, name = f.read(), target
    lines = content.splitlines()
    page = lines[offset : offset + max(1, limit)]
    result = {"name": name, "lines": len(lines), "content": "\n".join(page)}
    if offset + len(page) < len(lines):
        result["more"] = f"offset {offset + len(page)}"
    return result


@tool(
    "write_text",
    """Write a script: all of it (content) or by replacing a unique piece
    (replace: {"old": ..., "new": ...}). A text block that doesn't exist is
    created. Script nodes using it rebuild.""",
    {
        "node": {"type": "string"},
        "text": {"type": "string"},
        "file": {"type": "string"},
        "content": {"type": "string"},
        "replace": {"type": "object"},
    },
    writes=True,
)
def write_text(node="", text="", file="", content=None, replace=None):
    if (content is None) == (replace is None):
        raise ToolError("Give content or replace")
    kind, target = _target(node, text, file)
    block = None
    if kind == "text":
        block = (
            target if isinstance(target, bpy.types.Text) else bpy.data.texts.get(target)
        )
        if block is None:
            block = bpy.data.texts.new(target)
        current = block.as_string()
    else:
        current = ""
        if os.path.exists(target):
            with open(target, encoding="utf-8") as f:
                current = f.read()
    if replace is not None:
        old, new = replace.get("old", ""), replace.get("new", "")
        count = current.count(old) if old else 0
        if count != 1:
            raise ToolError(f"replace.old must appear once, it appears {count} times")
        content = current.replace(old, new)
    if block is not None:
        block.clear()
        block.write(content)
    else:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
    rebuilt = []
    for tree in scripting_node_trees():
        for script in sn_nodes(tree):
            if script.bl_idname != "SNA_Node_Script":
                continue
            uses = (block is not None and script.text_block == block) or (
                block is None
                and script.filepath
                and os.path.abspath(bpy.path.abspath(script.filepath)) == target
            )
            if uses:
                script.mark_dirty()
                rebuilt.append(script.id)
    return {
        "name": block.name if block else target,
        "lines": content.count("\n") + 1,
        "script_nodes": rebuilt,
    }
