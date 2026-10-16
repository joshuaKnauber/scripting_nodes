"""On Blender Change: runs when a property of Blender changes (bpy.msgbus),
e.g. the active object, an object's location or the render engine."""

import bpy

from ....blend_data import rna
from ....core import naming
from ....core.context import NodeError
from ....sockets.spec import Logic
from ..._blend_path import BlendPathMixin
from ...base_node import ScriptingBaseNode


class SNA_Node_OnBlenderChange(BlendPathMixin, ScriptingBaseNode, bpy.types.Node):
    """Runs when a Blender property changes in the interface: the active
    object (view_layer.objects.active), an object's location, the mode, ...
    It watches the property on every data of that type, not only the one
    the path leads to."""

    bl_idname = "SNA_Node_OnBlenderChange"
    bl_label = "On Blender Change"
    bl_width_default = 240
    sn_root = True
    sn_outputs = [Logic()]

    def path_accepts(self, step):
        # msgbus doesn't report items added to or removed from collections
        return not step.is_subscript and step.prop is not None and not step.collection

    def watched(self):
        """(struct name, property name) the path ends at, or None."""
        parts = self.path_parts()
        if not parts or parts[-1] == rna.SUBSCRIPT:
            return None
        steps = [self.path_root_step(), *self.path_steps()]
        owner, final = steps[-2], steps[-1]
        if not self.path_accepts(final) or not final.known:
            return None
        type_name = owner.collection_type if owner.collection else owner.rna_type
        # `width` of a modifier is a property of BevelModifier
        for candidate in (type_name, *rna.subtypes(type_name)):
            struct = rna.struct(candidate)
            if struct is not None and final.name in struct.properties:
                return candidate, final.name
        return None

    def sn_names(self):
        watched = self.watched()
        text = "_".join(watched) if watched else "blender"
        return [naming.Symbol("function", f"on_{naming.snake(text)}_change")]

    def draw(self, context, layout):
        self.draw_path(layout)
        watched = self.watched()
        if watched:
            layout.label(
                text=f"Any {rna.display_name(watched[0])} › {watched[1]}",
                icon="VIEWZOOM",
            )

    def emit(self, ctx):
        if self.path_root == "INPUT":
            raise NodeError("Start the path at the Context or the Blend File")
        watched = self.watched()
        if watched is None:
            raise NodeError("Search or paste a Blender property")
        function = ctx.name("function")
        ctx.module(f"""
            def {function}():
                {ctx.flow("flow")}
        """)
        struct, prop = watched
        ctx.on_register(f"{ctx.helper('subscribe')}({struct!r}, {prop!r}, {function})")
