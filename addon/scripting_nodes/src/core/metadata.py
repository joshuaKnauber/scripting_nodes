"""The add-on's metadata (settings/addon.py) as `blender_manifest.toml` (the
extension, when installed from the exported .zip) and `bl_info` (the live
add-on, a legacy add-on in the user's scripts folder).

Blender rejects a manifest with a tagline or permission reason longer than 64
characters or ending in punctuation; these are fixed when written, other
problems are listed by `problems()` (shown in the sidebar).
"""

import json
import re

# Blender's add-on tags (extensions platform)
TAGS = (
    "3D View",
    "Add Curve",
    "Add Mesh",
    "Animation",
    "Bake",
    "Camera",
    "Compositing",
    "Development",
    "Game Engine",
    "Geometry Nodes",
    "Grease Pencil",
    "Import-Export",
    "Lighting",
    "Material",
    "Mesh",
    "Modeling",
    "Node",
    "Object",
    "Paint",
    "Physics",
    "Pipeline",
    "Render",
    "Rigging",
    "Scene",
    "Sculpt",
    "Sequencer",
    "System",
    "Text Editor",
    "Tracking",
    "User Interface",
    "UV",
)

LICENSES = (
    ("SPDX:GPL-3.0-or-later", "GPL 3.0 or later", "GNU General Public License v3.0 or later"),
    ("SPDX:GPL-2.0-or-later", "GPL 2.0 or later", "GNU General Public License v2.0 or later"),
    ("SPDX:MIT", "MIT", "MIT License"),
    ("SPDX:BSD-3-Clause", "BSD 3-Clause", "BSD 3-Clause License"),
)  # fmt: skip

# (name, what it allows, reason used when none is given)
PERMISSIONS = (
    ("files", "Files", "Reads and writes files"),
    ("network", "Network", "Connects to the internet"),
    ("clipboard", "Clipboard", "Copies and pastes text"),
    ("camera", "Camera", "Records with the camera"),
    ("microphone", "Microphone", "Records with the microphone"),
)

DEFAULT_TAGLINE = "Add-on created with Scripting Nodes"
_COPYRIGHT = re.compile(r"\d{4}(-\d{4})? \S.*")


def short_text(text, fallback):
    """Text Blender accepts as tagline / reason: at most 64 characters, no
    punctuation at the end."""
    text = " ".join(text.split())[:64].rstrip(" .,;:!?")
    return text or fallback


def version(values) -> str:
    return ".".join(str(int(v)) for v in values)


def copyright(settings) -> str | None:
    """The copyright line, None if there is none or it isn't valid."""
    text = settings.copyright.strip()
    return text if _COPYRIGHT.fullmatch(text) else None


def version_max(settings) -> str | None:
    """The first Blender version that isn't supported, None if any is."""
    if not settings.use_blender_version_max:
        return None
    if tuple(settings.blender_version_max) <= tuple(settings.blender_version_min):
        return None
    return version(settings.blender_version_max)


def problems(settings) -> list[str]:
    """What's wrong with the metadata (fixed or left out when written)."""
    found = []
    if settings.copyright.strip() and copyright(settings) is None:
        found.append("Copyright must be 'Year Name' or 'Year-Year Name'")
    if settings.tagline and short_text(settings.tagline, "") != settings.tagline:
        found.append("Description: at most 64 characters, no punctuation at the end")
    if settings.use_blender_version_max and version_max(settings) is None:
        found.append("Blender maximum must be higher than the minimum")
    return found


def _toml(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def maintainer(settings) -> str:
    name = settings.author.strip() or "Unknown"
    email = settings.email.strip()
    return f"{name} <{email}>" if email else name


def manifest(settings) -> str:
    lines = [
        'schema_version = "1.0.0"',
        "",
        f"id = {_toml(settings.module_name)}",
        f"version = {_toml(version(settings.version))}",
        f"name = {_toml(settings.addon_name)}",
        f"tagline = {_toml(short_text(settings.tagline, DEFAULT_TAGLINE))}",
        f"maintainer = {_toml(maintainer(settings))}",
        'type = "add-on"',
    ]
    if settings.website.strip():
        lines.append(f"website = {_toml(settings.website.strip())}")
    if settings.tags:
        lines.append(f"tags = {_toml(sorted(settings.tags))}")
    lines += [
        "",
        f"blender_version_min = {_toml(version(settings.blender_version_min))}",
    ]
    if version_max(settings):
        lines.append(f"blender_version_max = {_toml(version_max(settings))}")
    lines += ["", f"license = [\n  {_toml(settings.license)},\n]"]
    if copyright(settings):
        lines.append(f"copyright = [\n  {_toml(copyright(settings))},\n]")
    permissions = [
        (name, short_text(getattr(settings, f"{name}_reason"), default))
        for name, _, default in PERMISSIONS
        if getattr(settings, f"permission_{name}")
    ]
    if permissions:
        lines += ["", "[permissions]"]
        lines += [f"{name} = {_toml(reason)}" for name, reason in permissions]
    lines += [
        "",
        "[build]",
        'paths_exclude_pattern = [\n  "__pycache__/",\n  ".*",\n  "*.zip",\n]',
    ]
    return "\n".join(lines) + "\n"


def bl_info(settings) -> str:
    """The `bl_info = {...}` of the add-on's __init__.py."""
    tags = sorted(settings.tags)
    info = {
        "name": settings.addon_name,
        "author": settings.author.strip() or "Unknown",
        "description": settings.tagline.strip() or DEFAULT_TAGLINE,
        "blender": tuple(settings.blender_version_min),
        "version": tuple(settings.version),
        "location": settings.location.strip(),
        "category": tags[0] if tags else "General",
    }
    if settings.website.strip():
        info["doc_url"] = settings.website.strip()
    body = "".join(f"    {key!r}: {value!r},\n" for key, value in info.items())
    return "bl_info = {\n" + body + "}"


def license_header(settings) -> str:
    lines = [f"# SPDX-License-Identifier: {settings.license.removeprefix('SPDX:')}"]
    if copyright(settings):
        lines.insert(0, f"# SPDX-FileCopyrightText: {copyright(settings)}")
    return "\n".join(lines)
