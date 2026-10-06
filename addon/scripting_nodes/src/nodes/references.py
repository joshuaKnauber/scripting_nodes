import bpy

from ..core.references import find_node


class SNA_NodeReference(bpy.types.PropertyGroup):
    """One entry of a picker collection on scene.sna (rebuilt every flush)."""

    name: bpy.props.StringProperty()

    node_id: bpy.props.StringProperty()

    @property
    def node(self):
        """The node this entry stands for, or None if it no longer exists."""
        return find_node(self.node_id)
