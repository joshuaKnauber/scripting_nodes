from scripting_nodes.src.features.nodes.categories.Groups.node_group_output import (
    SNA_Node_GroupOutput,
)
from scripting_nodes.src.features.nodes.categories.Groups.node_group_input import (
    SNA_Node_GroupInput,
)
import bpy
from scripting_nodes.src.features.node_tree.node_tree import ScriptingNodeTree
from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import node_by_id


class SNA_OT_AddGroup(bpy.types.Operator):
    bl_idname = "sna.add_group"
    bl_label = "Add Group"
    bl_description = "Add node group"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_id: bpy.props.StringProperty()

    def execute(self, context):
        group = bpy.data.node_groups.new("Node Group", ScriptingNodeTree.bl_idname)
        input_node = group.nodes.new(SNA_Node_GroupInput.bl_idname)
        input_node.location = (-200, 0)
        output_node = group.nodes.new(SNA_Node_GroupOutput.bl_idname)
        output_node.location = (200, 0)
        node = node_by_id(self.node_id)
        if node:
            node.group_tree = group
        return {"FINISHED"}


class SNA_OT_EditSerpensGroup(bpy.types.Operator):
    bl_idname = "sna.edit_group"
    bl_label = "Edit Node Group"
    bl_description = "Edit a node group"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    always_quit: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return (
            getattr(context.space_data, "tree_type", None)
            == ScriptingNodeTree.bl_idname
        )

    def execute(self, context):
        path = context.space_data.path
        if (
            context.active_node
            and context.active_node.select
            and hasattr(context.active_node, "group_tree")
            and not self.always_quit
        ):
            tree = context.active_node.group_tree
            if tree:
                path.append(tree)
        elif len(path) > 1:
            path.pop()
        return {"FINISHED"}
