import bpy


class ScriptingNodesTree(bpy.types.NodeTree):
    bl_idname = "ScriptingNodeTree"
    bl_label = "Scripting Node Editor"
    bl_icon = "FILE_SCRIPT"
    is_sn = True
    type: bpy.props.EnumProperty(
        items=[("SCRIPTING", "Scripting", "Scripting")], name="Type"
    )

    is_dirty: bpy.props.BoolProperty(default=False, name="Is Dirty")

    def update(self):
        """ Called when the node tree is updating. """
        # TODO maybe remove it not needed

    def mark_dirty(self, node: bpy.types.Node):
        self.is_dirty = True

    def _execute_node(self, node_id: str, local_vars: dict, global_vars: dict):
        """ Runs the generated code on the given node. Called by nodes during development. """
        for node in self.nodes:
            if getattr(node, "id", None) == node_id:
                node._execute(local_vars, global_vars)
                break
