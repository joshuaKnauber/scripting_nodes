def node_header(self, context):
    if context.space_data.node_tree:
        if context.space_data.node_tree.bl_idname == "ScriptingNodesTree":
            self.layout.operator("scripting_nodes.compile_active")
            self.layout.prop(context.scene.sn_properties,"auto_compile")