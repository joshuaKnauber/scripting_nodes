"""
Operators for creating and editing group node trees.
"""

from ..node_group_output import (
    SNA_Node_GroupOutput,
)
from ..node_group_input import (
    SNA_Node_GroupInput,
)
import bpy
from .....node_tree.node_tree import ScriptingNodeTree
from ......lib.utils.node_tree.scripting_node_trees import node_by_id


class SNA_OT_AddGroup(bpy.types.Operator):
    bl_idname = "sna.add_group"
    bl_label = "Add Group"
    bl_description = "Create a new node group"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_id: bpy.props.StringProperty()

    def execute(self, context):
        # Create the group node tree
        group_tree = bpy.data.node_groups.new("Group", ScriptingNodeTree.bl_idname)
        group_tree.is_group = True

        # Add input and output nodes
        input_node = group_tree.nodes.new(SNA_Node_GroupInput.bl_idname)
        input_node.location = (-200, 0)
        output_node = group_tree.nodes.new(SNA_Node_GroupOutput.bl_idname)
        output_node.location = (200, 0)

        # Link input to output (default is Logic)
        group_tree.links.new(input_node.outputs["Logic"], output_node.inputs["Logic"])

        # Assign to calling node if provided
        node = node_by_id(self.node_id)
        if node and hasattr(node, "group_tree"):
            node.group_tree = group_tree

        return {"FINISHED"}


class SNA_OT_EditGroup(bpy.types.Operator):
    bl_idname = "sna.edit_group"
    bl_label = "Edit Group"
    bl_description = "Edit a group (Tab to enter, Tab again to exit)"
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

        # Try to enter a group
        if (
            context.active_node
            and context.active_node.select
            and hasattr(context.active_node, "group_tree")
            and not self.always_quit
        ):
            tree = context.active_node.group_tree
            if tree:
                path.append(tree)
        # Or exit current group
        elif len(path) > 1:
            path.pop()

        return {"FINISHED"}
