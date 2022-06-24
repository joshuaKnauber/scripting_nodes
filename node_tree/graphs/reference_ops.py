import bpy


class SN_OT_FindReferencingNodes(bpy.types.Operator):
    bl_idname = "sn.find_referencing_nodes"
    bl_label = "Find Referencing Nodes"
    bl_description = "Find all nodes that reference this node"
    bl_options = {'REGISTER', 'UNDO', "INTERNAL"}
    
    node: bpy.props.StringProperty(name="Node", options={'HIDDEN', 'SKIP_SAVE'})
    
    references = {}

    def execute(self, context):
        pass
        
    def draw(self, context):
        layout = self.layout
        
        for key in self.references:
            layout.label(text=key)
            for ref in self.references[key]:
                op = layout.operator("sn.find_node", text=ref, icon="RESTRICT_SELECT_OFF")
                op.node_tree = key
                op.node = ref
            layout.separator()
            
        if not self.references:
            layout.label(text="No references found", icon="INFO")
                
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