def node_header(self, context):
    if context.space_data.node_tree:
        if context.space_data.node_tree.bl_idname == "ScriptingNodesTree":
            if context.space_data.node_tree.nodes.active:
                self.layout.prop(context.scene.sn_properties,"show_node_info",text="", icon="QUESTION", toggle=True)
                self.layout.prop(context.scene.sn_properties,"tutorial_scale",text="Scale", slider=True)

            row = self.layout.row(align=True)
            row.operator("scripting_nodes.compile_active", icon="FILE_REFRESH")
            row.operator("scripting_nodes.unregister_active", text="", icon="UNLINKED")
            row.separator()
    if context.space_data.tree_type == "ScriptingNodesTree":
        self.layout.prop(context.scene.sn_properties,"examples",text="")