"""Scripts: text blocks and files of the add-on's scripts (Addon Data ›
Scripts) and of Inline Script nodes."""

import os

import bpy

from ...core import folders, scheduler
from ...core import scripts as script_list
from ...lib.ids import get_short_id
from ...lib.trees import scripting_node_trees, sn_nodes
from . import tool
from ._common import ToolError, find_node

_LIMIT = 400


def _owner(node):
    """What has the script of `node`: an Inline Script node itself, the list
    script of a Script Function."""
    if node.bl_idname == "SNA_Node_ScriptFunction":
        return node.script_item()
    return node if node.bl_idname == "SNA_Node_InlineScript" else None


def _find_script(label):
    for text, script in script_list.choices():
        if text == label:
            return script
    names = [text for text, _ in script_list.choices()]
    raise ToolError(f"No script {label!r} in the add-on. Scripts: {names}")


def _target(node="", script="", text="", file=""):
    """("text", block) or ("file", path) of what to read / write."""
    if sum(bool(x) for x in (node, script, text, file)) != 1:
        raise ToolError("Give one of node, script, text or file")
    if node or script:
        if node:
            found = find_node(node)
            owner = _owner(found)
            if owner is None:
                raise ToolError(
                    f"{found.name!r} isn't an Inline Script or Script Function node"
                )
        else:
            owner = _find_script(script)
        if owner.source_type == "INTERNAL":
            if owner.text_block is None:
                raise ToolError("It has no text block: pick one")
            return "text", owner.text_block
        if not owner.filepath:
            raise ToolError("It has no file: set its filepath")
        return "file", bpy.path.abspath(owner.filepath)
    if text:
        return "text", text
    return "file", os.path.abspath(bpy.path.abspath(file))


def _uses(owner, block, path):
    if block is not None:
        return owner.source_type == "INTERNAL" and owner.text_block == block
    return (
        owner.source_type == "EXTERNAL"
        and bool(owner.filepath)
        and os.path.abspath(bpy.path.abspath(owner.filepath)) == path
    )


@tool(
    "edit_scripts",
    """Add scripts to the add-on or remove them (the Files list). A script of
    the add-on is part of it unchanged: its classes are registered, its
    register() / unregister() called. Script Function nodes call its
    functions: set their "script" (the label listed here) and "function".
    Write the code with write_text first. "folder" is its package, like a
    tree's ("UI/Helpers" -> ui/helpers/tools.py, "" the top level); scripts
    without one go to "Scripts" (scripts/tools.py).

    add: [{"text": "tools.py", "folder": "Scripts"}] or [{"file": "//tools.py"}]
    remove: ["tools.py"]""",
    {
        "add": {"type": "array", "items": {"type": "object"}},
        "remove": {"type": "array", "items": {"type": "string"}},
    },
    writes=True,
)
def edit_scripts(add=(), remove=()):
    addon = bpy.context.scene.sna.addon
    for label in remove:
        script = _find_script(label)
        callers = script_list.callers(script)
        index = next(i for i, s in enumerate(addon.scripts) if s.id == script.id)
        addon.scripts.remove(index)
        for node in callers:
            node.mark_dirty()
    for spec in add:
        text, file = spec.get("text", ""), spec.get("file", "")
        if bool(text) == bool(file):
            raise ToolError('Each script needs "text" or "file"')
        if text and text not in bpy.data.texts:
            raise ToolError(f"No text block {text!r}: write it with write_text first")
        script = addon.scripts.add()
        script.id = get_short_id()
        if "folder" in spec:
            path = folders.split(spec["folder"])
            script.folder = folders.join(*(folders.clean_name(p) for p in path))
            folders.add(script.folder)
        if text:
            script.text_block = bpy.data.texts[text]
        else:
            script.source_type = "EXTERNAL"
            script.filepath = file
    scheduler.request_full()
    return {
        "scripts": [
            {
                "script": label,
                "folder": script.folder,
                "functions": script.script_functions(),
            }
            for label, script in script_list.choices()
        ]
    }


@tool(
    "read_text",
    """Read a script: of a script of the add-on (its label), an Inline Script
    or Script Function node, a text block by name or a file. Long texts come
    in pages of lines (offset, limit).""",
    {
        "node": {"type": "string"},
        "script": {"type": "string"},
        "text": {"type": "string"},
        "file": {"type": "string"},
        "offset": {"type": "integer"},
        "limit": {"type": "integer"},
    },
)
def read_text(node="", script="", text="", file="", offset=0, limit=_LIMIT):
    kind, target = _target(node, script, text, file)
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
    created. Nodes and scripts using it rebuild.""",
    {
        "node": {"type": "string"},
        "script": {"type": "string"},
        "text": {"type": "string"},
        "file": {"type": "string"},
        "content": {"type": "string"},
        "replace": {"type": "object"},
    },
    writes=True,
)
def write_text(node="", script="", text="", file="", content=None, replace=None):
    if (content is None) == (replace is None):
        raise ToolError("Give content or replace")
    kind, target = _target(node, script, text, file)
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
    for script in script_list.scripts():
        if _uses(script, block, target):
            script_list.changed(script)
            rebuilt.append(script_list.label(script))
    for tree in scripting_node_trees():
        for node in sn_nodes(tree):
            if node.bl_idname == "SNA_Node_InlineScript" and _uses(node, block, target):
                node.mark_dirty()
                rebuilt.append(node.id)
    return {
        "name": block.name if block else target,
        "lines": content.count("\n") + 1,
        "rebuilt": rebuilt,
    }
