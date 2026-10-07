"""Addon Preferences: the `bpy.types.AddonPreferences` class of the generated
addon. Properties with register_on = Preferences that are attached to it
become its settings, the Draw flow lays out the preferences UI.

Only one per addon makes sense (Blender allows one preferences class per
addon); extra ones fail to register.
"""

import bpy

from ....sockets.spec import Interface
from ..._class_body import ClassBodyContainerMixin
from ..._reference_signatures import PROPERTY_NODES
from ...base_node import ScriptingBaseNode


class SNA_Node_Preferences(ClassBodyContainerMixin, ScriptingBaseNode, bpy.types.Node):
    """The preferences of the addon (shown in Preferences > Add-ons)."""

    bl_idname = "SNA_Node_Preferences"
    bl_label = "Preferences"
    sn_root = True
    sn_class_body_signature = PROPERTY_NODES
    sn_class_body_target = "Preferences"
    sn_outputs = [Interface("draw", "Draw")]

    def draw(self, context, layout):
        self.draw_class_body_properties(layout, label="Properties")

    def emit(self, ctx):
        # bl_idname must be the addon's package: tree modules live in
        # <addon>/addon/<tree>.py, so drop the last part of __package__
        ctx.module(f"""
            class {ctx.class_name("AP", "Preferences")}(bpy.types.AddonPreferences):
                bl_idname = __package__.rsplit(".", 1)[0]
                {ctx.join(self.annotations(ctx))}

                def draw(self, context):
                    {ctx.flow("draw", layout="self.layout")}
        """)
