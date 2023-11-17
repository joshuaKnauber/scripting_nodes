import bpy


class NodePointer(bpy.types.PropertyGroup):
    @property
    def node(self):
        """Get the referenced node"""
        for ntree in bpy.data.node_groups:
            if getattr(ntree, "is_sn_ntree", False):
                for node in ntree.nodes:
                    if getattr(node, "id", None) == self.id:
                        return node
        return None

    def update_name(self, context):
        """Update the referenced node"""
        sna = context.scene.sna
        ref = sna.references.get_ref_by_node_name(self.name)
        if ref is not None:
            self.id = ref.id
        else:
            self.id = ""
        # TODO mark node as dirty
        for ntree in bpy.data.node_groups:
            if getattr(ntree, "is_sn_ntree", False):
                for node in ntree.nodes:
                    if getattr(node, "is_sn_node", False):
                        node.mark_dirty()

    name: bpy.props.StringProperty(
        name="Name",
        default="",
        description="Name of the referenced node",
        update=update_name,
    )
    id: bpy.props.StringProperty(
        name="ID", default="", description="ID of the referenced node"
    )


def collection(idname: str):
    """Returns the collection for the given idname"""
    sna = bpy.context.scene.sna
    return sna.references.get_collection(idname)


def node_search(layout: bpy.types.UILayout, prop: NodePointer, idname: str):
    """Draws a node search field"""
    coll = collection(idname)
    if coll:
        layout.prop_search(prop, "name", coll, "nodes", text="")
    else:  # draw dummy prop search
        subrow = layout.row()
        subrow.enabled = False
        subrow.prop_search(prop, "name", bpy.data.node_groups[0], "nodes", text="")


def get_references_to_node(node: bpy.types.Node):
    """Returns a list of references to the given node"""
    refs = []
    for ntree in bpy.data.node_groups:
        if getattr(ntree, "is_sn_ntree", False):
            for ref_node in ntree.nodes:
                for prop in ref_node.bl_rna.properties:
                    if (
                        getattr(prop, "fixed_type", None)
                        and prop.fixed_type.identifier == NodePointer.__name__
                    ):
                        if getattr(ref_node, prop.identifier).id == node.id:
                            refs.append(ref_node)
    return refs
