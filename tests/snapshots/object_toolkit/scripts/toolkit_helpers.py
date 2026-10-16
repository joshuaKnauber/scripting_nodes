"""Helpers of the Object Toolkit."""

import bpy


def select_objects(names: str) -> int:
    """Select the objects named in a comma separated list."""
    count = 0
    for name in names.split(","):
        obj = bpy.context.scene.objects.get(name.strip())
        if obj is not None:
            obj.select_set(True)
            count += 1
    return count
