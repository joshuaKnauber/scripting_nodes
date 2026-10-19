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
from ..lib.trees import node_by_id
from ..settings.properties import (
    TYPE_ICONS,
    SNA_PropertyMember,
    draw_list,
    draw_settings,
)
from ..sockets.spec import Socket

OUTPUT_PREFIX = "prop_"
# scope value: the operator / preferences themselves, in their own methods
SELF = "__self__"


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
        """The properties' names on the node, and a button editing them in a
        popup (also in the sidebar's Node tab)."""
        col = layout.column(align=True)
        for prop in self.properties:
            col.label(text=prop.name, icon=TYPE_ICONS.get(prop.property_type, "DOT"))
        text = "Edit Properties" if len(self.properties) else "Add Properties"
        op = col.operator("sna.edit_node_properties", text=text, icon="PROPERTIES")
        op.node_id = self.id

    def draw_buttons_ext(self, context, layout):
        self.draw_buttons(context, layout)
        layout.separator()
        prop = draw_list(layout, "NODE", self.id)
        if prop is not None:
            draw_settings(layout.column(), prop, on_node=True)


class SNA_OT_EditNodeProperties(bpy.types.Operator):
    """Add and edit the properties of this node (also in the sidebar's Node
    tab while the node is selected)"""

    bl_idname = "sna.edit_node_properties"
    bl_label = "Properties"
    bl_options = {"INTERNAL"}

    node_id: bpy.props.StringProperty(options={"HIDDEN"})

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=380)

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        node = node_by_id(self.node_id)
        if node is None:
            return
        layout = self.layout
        layout.label(text=f"{node.name}: Properties")
        prop = draw_list(layout, "NODE", node.id)
        if prop is not None:
            draw_settings(layout.column(), prop, on_node=True)
