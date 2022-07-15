import bpy


class SN_OT_FindReferencingNodes(bpy.types.Operator):
    bl_idname = "sn.find_referencing_nodes"
    bl_label = "Find Referencing Nodes"
    bl_description = "Find all nodes that reference this node"
    bl_options = {'REGISTER', 'UNDO', "INTERNAL"}
    
    node: bpy.props.StringProperty(name="Node", options={'HIDDEN', 'SKIP_SAVE'})
    add_node: bpy.props.StringProperty(name="Add Node", options={'HIDDEN', 'SKIP_SAVE'})
    
    references = {}

    def execute(self, context):
        pass
        
    def draw(self, context):
        layout = self.layout
        if not self.node in context.space_data.node_tree.nodes: return
        ref_node = context.space_data.node_tree.nodes[self.node]
        
        for key in self.references:
            layout.label(text=key)
            for ref in self.references[key]:
                op = layout.operator("sn.find_node", text=ref, icon="RESTRICT_SELECT_OFF")
                op.node_tree = key
                op.node = ref
            layout.separator()
            
        if not self.references:
            layout.label(text="No references found", icon="INFO")
        
        if self.add_node:
            op = layout.operator("sn.add_referencing_node", text="Add Node", icon="FORWARD")
            op.idname = self.add_node
            key = ref_node.bl_idname if not ref_node.collection_key_overwrite else ref_node.collection_key_overwrite
            op.ref_attr = f"ref_{key}"
            op.node = ref_node.name
                
    def invoke(self, context, event):
        self.references = {}
        ref_node = context.space_data.node_tree.nodes[self.node]
        for ngroup in bpy.data.node_groups:
            for node in ngroup.nodes:
                idname = ref_node.collection_key_overwrite if ref_node.collection_key_overwrite else ref_node.bl_idname
                if getattr(node, f"ref_{idname}", None) == ref_node.name and getattr(node, "ref_ntree", None) == ref_node.node_tree:
                    if not ngroup.name in self.references:
                        self.references[ngroup.name] = []
                    self.references[ngroup.name].append(node.name)
        return context.window_manager.invoke_popup(self, width=250)	
    
    
    
class SN_OT_AddReferencingNode(bpy.types.Operator):
    bl_idname = "sn.add_referencing_node"
    bl_label = "Add Node"
    bl_description = "Adds the referenced node to the node tree"
    bl_options = {"REGISTER", "INTERNAL"}

    idname: bpy.props.StringProperty(name="ID Name", options={'HIDDEN', 'SKIP_SAVE'})
    ref_attr: bpy.props.StringProperty(name="Attribute", options={'HIDDEN', 'SKIP_SAVE'})
    node: bpy.props.StringProperty(name="Node", options={'HIDDEN', 'SKIP_SAVE'})

    def execute(self, context):
        bpy.ops.node.add_node("INVOKE_DEFAULT", type=self.idname, use_transform=True)
        node = context.space_data.node_tree.nodes.active
        setattr(node, self.ref_attr, self.node)
        return {"FINISHED"}
