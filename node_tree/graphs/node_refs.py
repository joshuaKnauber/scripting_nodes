import bpy


node_cache = (
    {}
)  # stores a cache of the nodes with key f"{node_tree.name};{node.static_uid}"


class NodeRef(bpy.types.PropertyGroup):

    @property
    def node(self):
        node_tree = self.id_data
        # retrieve node from cache
        if f"{node_tree.name};{self.uid}" in node_cache:
            return node_cache[f"{node_tree.name};{self.uid}"]
        # save node to cache
        for node in node_tree.nodes:
            if getattr(node, "static_uid", None) == self.uid:
                node_cache[f"{node_tree.name};{node.static_uid}"] = node
                return node
        return None

    def update_name(self, context):
        """Called when name changes - update references in other nodes"""
        prev_name = self.prev_name
        new_name = self.name

        if prev_name and prev_name != new_name:
            ref_node = self.node
            if ref_node:
                for ntree in bpy.data.node_groups:
                    if ntree.bl_idname == "ScriptingNodesTree":
                        for node in ntree.nodes:
                            if getattr(node, "ref_ntree", None) == ref_node.node_tree:
                                # update specific node type references
                                if (
                                    getattr(
                                        node, f"ref_{ref_node.collection_key}", None
                                    )
                                    == prev_name
                                ):
                                    setattr(
                                        node, f"ref_{ref_node.collection_key}", new_name
                                    )
                                # update node names for any type of node
                                elif getattr(node, "from_node", None) == prev_name:
                                    setattr(node, f"from_node", new_name)

        self.prev_name = new_name

    # The static_uid of the node that belongs to this reference
    uid: bpy.props.StringProperty(
        name="UID",
        description="The static_uid of the node that belongs to this reference",
    )

    # Track previous name for reference updates
    prev_name: bpy.props.StringProperty()

    name: bpy.props.StringProperty(
        name="Name",
        description="The name of the node this reference belongs to",
        update=update_name,
    )


class NodeRefCollection(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(
        name="Node Name", description="The idname of the nodes in this collection"
    )

    refs: bpy.props.CollectionProperty(
        type=NodeRef,
        name="References",
        description="References to the nodes of this type",
    )

    def get_ref_by_uid(self, uid):
        for ref in self.refs:
            if ref.uid == uid:
                return ref
        return None

    def clear_unused_refs(self):
        """Removes all references that don't match a node"""
        for i in range(len(self.refs) - 1, -1, -1):
            if not self.refs[i].node:
                self.refs.remove(i)

    def fix_ref_names(self):
        """Makes sure all ref names match the node names"""
        for ref in self.refs:
            node = ref.node
            if node and ref.name != node.name:
                ref.name = node.name
                node.on_node_name_change()
                # node._evaluate(bpy.context)

    @property
    def nodes(self):
        """Returns all the nodes for this collection"""
        return [ref.node for ref in self.refs]
