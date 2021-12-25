import bpy



class NodeRef(bpy.types.PropertyGroup):
    
    @property
    def node(self):
        node_tree = self.id_data # TODO optimize
        for node in node_tree.nodes:
            if node.static_uid == self.uid:
                return node
    
    uid: bpy.props.StringProperty(name="UID",
                                description="The static_uid of the node that belongs to this reference")
    
    name: bpy.props.StringProperty(name="Name",
                                description="The name of the node this reference belongs to")



class NodeRefCollection(bpy.types.PropertyGroup):
    
    name: bpy.props.StringProperty(name="Node Name",
                                description="The idname of the nodes in this collection")
    
    refs: bpy.props.CollectionProperty(type=NodeRef,
                                name="References",
                                description="References to the nodes of this type")
    
    @property
    def nodes(self):
        """ Returns all the nodes for this collection """
        return [ref.node for ref in self.refs]
