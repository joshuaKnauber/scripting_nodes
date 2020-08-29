def node_header(self, context):
    if context.space_data.node_tree:
        if context.space_data.node_tree.bl_idname == "ScriptingNodesTree":
            if context.space_data.node_tree.nodes.active:
                op = self.layout.operator("scripting_nodes.draw_tutorial", text=" Show Node Info", icon="QUESTION").show_node_info = True

            row = self.layout.row(align=True)
            row.operator("scripting_nodes.compile_active", icon="FILE_REFRESH")
            row.operator("scripting_nodes.unregister_active", text="", icon="UNLINKED")
            row.separator()
    if context.space_data.tree_type == "ScriptingNodesTree":
        self.layout.prop(context.scene.sn_properties,"examples",text="")