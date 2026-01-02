from ....lib.utils.node_tree.scripting_node_trees import (
    node_by_id,
    scripting_node_trees,
    sn_nodes,
)
import bpy


class SNA_NodeReference(bpy.types.PropertyGroup):

    def get_name(self):
        return self["name"]

    def set_name(self, value):
        curr_value = self["name"] if "name" in self else ""
        # keep node references up-to-date
        for ntree in scripting_node_trees():
            for node in sn_nodes(ntree):
                for prop in node.sn_reference_properties:
                    if hasattr(node, prop) and getattr(node, prop, "") == curr_value:
                        node[prop] = value
        self["name"] = value

    # name: bpy.props.StringProperty(get=get_name, set=set_name)
    name: bpy.props.StringProperty()

    node_id: bpy.props.StringProperty()

    @property
    def node(self):
        """Returns the node that created this reference."""
        return node_by_id(self.node_id)
