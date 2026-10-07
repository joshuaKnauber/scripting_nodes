"""Identifiers of generated classes, operators and functions.

Derived from the node id, so other nodes can compute the same name (a Button
needs the idname of the Operator node it calls).
"""

import re

import bpy


def addon_settings():
    return bpy.context.scene.sna.addon


def identifier(text: str, fallback: str = "item") -> str:
    """A valid Python identifier made from user text."""
    text = re.sub(r"[^a-zA-Z0-9_]", "_", text or "")
    text = re.sub(r"_+", "_", text).strip("_")
    if not text:
        text = fallback
    if text[0].isdigit():
        text = "_" + text
    return text


def class_name(node, kind: str, label: str = "") -> str:
    """e.g. MY_ADDON_PT_Panel_1A2B3C4D5E (kind: PT, OT, MT, PG, AP, ...)."""
    parts = [addon_settings().class_prefix, kind]
    if label:
        parts.append(identifier(label))
    parts.append(node.id)
    return "_".join(parts)


def idname(node, name: str) -> str:
    """e.g. my_addon.operator_1a2b3c4d5e"""
    return f"{addon_settings().idname_namespace}.{name}_{node.id.lower()}"


def function_name(node, name: str) -> str:
    """e.g. update_value_1a2b3c4d5e"""
    return f"{identifier(name)}_{node.id.lower()}"
