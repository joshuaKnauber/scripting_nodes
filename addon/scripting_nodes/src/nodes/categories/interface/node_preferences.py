"""Addon Preferences: the `bpy.types.AddonPreferences` class of the generated
addon. Its properties (sidebar) are the add-on's settings, the Draw flow lays
out the preferences UI.

Only one per addon makes sense (Blender allows one preferences class per
addon); extra ones fail to register.
"""

import bpy

from ....core import naming
from ....sockets.spec import Interface
from ..._property_list import PropertyListMixin
from ...base_node import ScriptingBaseNode


# scope value: the preferences themselves, in their draw()
SELF = "__self__"


class SNA_Node_Preferences(PropertyListMixin, ScriptingBaseNode, bpy.types.Node):
    """The preferences of the addon (shown in Preferences > Add-ons)."""

    bl_idname = "SNA_Node_Preferences"
    bl_label = "Preferences"
    sn_root = True
    sn_outputs = [Interface("draw", "Draw")]

    def sn_names(self):
        return [naming.Class("class", "AP", "preferences")]

    def draw(self, context, layout):
        self.draw_property_names(layout)

    def emit(self, ctx):
        # its fields get `self` as the preferences in draw (_property_target)
        # bl_idname must be the add-on's package, the one of tree modules
        ctx.module(f"""
            class {ctx.name("class")}(bpy.types.AddonPreferences):
                bl_idname = __package__
                {ctx.join(self.annotations(ctx))}

                def draw(self, context):
                    {ctx.flow("draw", layout="self.layout", outputs={SELF: "self"})}
        """)
