from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import (
    scripting_node_trees,
    sn_nodes,
)
import bpy


class SNA_NodeReference(bpy.types.PropertyGroup):
    # Blender 5.0: get/set renamed to get_transform/set_transform in bpy.props
    # Changed to use update callback instead to avoid signature changes

    def update_name(self, context):
        # Get current value before updating (from shadow storage)
        curr_value = self.get("_name_old", "")
        
        # Keep node references up-to-date across all node trees
        for ntree in scripting_node_trees():
            for node in sn_nodes(ntree):
                for prop in node.sn_reference_properties:
                    if hasattr(node, prop) and getattr(node, prop, "") == curr_value:
                        node[prop] = self.name
        
        # Store shadow copy for next update (pure custom property, not bpy.props)
        self["_name_old"] = self.name

    name: bpy.props.StringProperty(update=update_name)

    node_id: bpy.props.StringProperty()
