"""Nodes with their own properties (Operator, Preferences): a list on the
node, edited in the sidebar's Node tab, written as annotations of the
node's class.

    class SNA_Node_Operator(PropertyListMixin, ScriptingBaseNode, bpy.types.Node):
        def emit(self, ctx):
            ... {ctx.join(self.annotations(ctx))} ...

`property_outputs()` gives one data output per property (`self.<name>`) for
nodes whose flows run inside the class.
"""

import bpy

from ..core import properties
from ..lib.ids import get_short_id
from ..settings.properties import SNA_PropertyMember, draw_list, draw_settings
from ..sockets.spec import Socket

OUTPUT_PREFIX = "prop_"


class PropertyListMixin:
    properties: bpy.props.CollectionProperty(type=SNA_PropertyMember)
    active_property: bpy.props.IntProperty()

    def copy(self, node):
        super().copy(node)
        for prop in self.properties:  # a copy gets its own properties
            prop.id = get_short_id()

    # -- code -----------------------------------------------------------------

    def annotations(self, ctx):
        return properties.node_annotations(self, ctx)

    def property_outputs(self):
        """A data output per property: its value inside the class's flows."""
        specs = []
        for prop in self.properties:
            if prop.property_type == "GROUP":
                continue
            spec = Socket(
                properties.socket_type(prop), OUTPUT_PREFIX + prop.id, prop.name
            )
            spec.attrs.update(properties.socket_attrs(prop))
            specs.append(spec)
        return specs

    def property_values(self):
        """{output key: expression} for ctx.flow(outputs=...)."""
        names = properties.python_names(self.properties)
        return {OUTPUT_PREFIX + pid: f"self.{name}" for pid, name in names.items()}

    # -- UI -------------------------------------------------------------------

    def draw_property_names(self, layout):
        """Compact list on the node; editing happens in the sidebar."""
        if not len(self.properties):
            layout.label(text="Properties: sidebar (N)", icon="INFO")

    def draw_buttons_ext(self, context, layout):
        self.draw_buttons(context, layout)
        layout.separator()
        prop = draw_list(layout, "NODE", self.id)
        if prop is not None:
            draw_settings(layout.column(), prop)
