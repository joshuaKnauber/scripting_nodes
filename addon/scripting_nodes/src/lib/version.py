import os
import tomllib

_MANIFEST = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "blender_manifest.toml",
)


def addon_version() -> str:
    """Scripting Nodes version from blender_manifest.toml (single source of truth)."""
    with open(_MANIFEST, "rb") as f:
        return tomllib.load(f)["version"]
