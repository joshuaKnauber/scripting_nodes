import bpy
from bpy.types import AddonPreferences


def _get_addon_name():
    """Get the addon name for bl_idname.

    For extensions: bl_ext.<repo>.<name> -> bl_ext.<repo>.<name>
    For legacy addons: scripting_nodes.src... -> scripting_nodes
    """
    parts = __package__.split(".")
    if parts[0] == "bl_ext" and len(parts) >= 3:
        return ".".join(parts[:3])
    else:
        return parts[0]


_addon_name = _get_addon_name()


class SNA_AddonPreferences(AddonPreferences):
    """Scripting Nodes addon preferences"""

    bl_idname = _addon_name

    def draw(self, context):
        layout = self.layout
        layout.label(text="No preferences yet.")


def get_preferences() -> SNA_AddonPreferences:
    """Get the addon preferences"""
    return bpy.context.preferences.addons[_addon_name].preferences
