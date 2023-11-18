import bpy


def _make_node_name(node: bpy.types.Node):
    """Returns an understandable name for the given node"""
    return f"{node.name} ({node.node_tree.name})"


def _split_node_name(name: str):
    """Splits a node name into the node name and the node tree name"""
    if " (" not in name:
        return "", ""
    parts = name.split(" (", 1)
    return parts[0], parts[1][:-1]


class SNA_NodeReference(bpy.types.PropertyGroup):
    def set_name(self, new_name: str):
        """Sets the name of the node and updates all nodes referencing this"""
        for ntree in bpy.data.node_groups:
            if getattr(ntree, "is_sn_tree", False):
                for node in ntree.nodes:
                    if getattr(node, "is_sn_node", False):
                        for prop in node.bl_rna.properties:
                            # refers to NodePointer which is used as a pointer on nodes
                            if (
                                prop.type == "POINTER"
                                and prop.fixed_type.name == "NodePointer"
                            ):
                                if getattr(node, prop.identifier).id == self.id:
                                    getattr(node, prop.identifier).name = new_name
        self["name"] = new_name

    def get_name(self):
        """Returns the name of the node"""
        return self.get("name", "")

    name: bpy.props.StringProperty(
        name="Name",
        default="",
        description="Name of the referenced node",
        set=set_name,
        get=get_name,
    )

    id: bpy.props.StringProperty(
        name="ID", default="", description="ID of the referenced node"
    )

    def get_node(self):
        """Returns the node with the given id"""
        for ntree in bpy.data.node_groups:
            if getattr(ntree, "is_sn_ntree", False):
                for node in ntree.nodes:
                    if getattr(node, "is_sn_node") and node.id == self.id:
                        return node
        return None


class SNA_NodeCollection(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="ID Name", default="", description="ID Name of the node type"
    )

    nodes: bpy.props.CollectionProperty(type=SNA_NodeReference)

    def get_ref_by_id(self, id: str) -> bpy.types.Node | None:
        """Returns the node with the given id"""
        for ref in self.nodes:
            if ref.id == id:
                return ref
        return None


class SNA_Nodes(bpy.types.PropertyGroup):
    collections: bpy.props.CollectionProperty(type=SNA_NodeCollection)

    def get_collection(self, idname: str) -> SNA_NodeCollection | None:
        """Returns the node collection for the given idname"""
        for collection in self.collections:
            if collection.name == idname:
                return collection
        return None

    def get_ref_by_node_name(self, name: str) -> bpy.types.Node | None:
        """Returns the ref with the given node name"""
        name, tree_name = _split_node_name(name)
        if tree_name in bpy.data.node_groups:
            tree = bpy.data.node_groups[tree_name]
            if name in tree.nodes:
                node = tree.nodes[name]
                collection = self.get_collection(node.bl_idname)
                if collection is not None:
                    return collection.get_ref_by_id(node.id)
        return None

    def add_reference(self, node: bpy.types.Node):
        """Updates or creates a reference"""
        collection = self.get_collection(node.bl_idname)
        if collection is None:
            collection = self.collections.add()
            collection.name = node.bl_idname
        ref = collection.nodes.add()
        ref.id = node.id
        ref.name = _make_node_name(node)

    def remove_reference(self, node: bpy.types.Node):
        """Removes a reference"""
        collection = self.get_collection(node.bl_idname)
        for i, ref in enumerate(collection.nodes):
            if ref.id == node.id:
                collection.nodes.remove(i)
                if len(collection.nodes) == 0:
                    self.collections.remove(self.collections.find(collection.name))
                return

    def update_ref_names_for_node(self, idname: str):
        """Updates the names of the nodes in the given collection"""
        collection = self.get_collection(idname)
        if collection is None:
            return
        for ref in collection.nodes:
            node = ref.get_node()
            if node is not None:
                ref.name = _make_node_name(node)

    def update_ref_names_by_ntree(self):
        """Updates the node tree names for all nodes"""
        for collection in self.collections:
            for ref in collection.nodes:
                node = ref.get_node()
                if node is not None:
                    ref.name = _make_node_name(node)
