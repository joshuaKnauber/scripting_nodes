"""Operators that create / manage group trees from the UI."""
import bpy


class SNA_OT_NewGroup(bpy.types.Operator):
    """Create a new node group (function) with default Input/Output nodes."""

    bl_idname = "sna.new_group"
    bl_label = "New Group"
    bl_description = (
        "Create a new node group (function) pre-populated with Group Input and "
        "Group Output nodes, and switch the editor to it"
    )
    bl_options = {"REGISTER", "UNDO"}

    name: bpy.props.StringProperty(name="Name", default="Group")
    # Captured at invoke time so the props-dialog context-swap doesn't lose it
    target_node_name: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})
    target_tree_name: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    def invoke(self, context, event):
        # Capture the calling Call Group node now - by execute() the dialog
        # has taken over context and context.active_node may not match.
        active = getattr(context, "active_node", None)
        if active and active.bl_idname == "SNA_Node_Group":
            self.target_node_name = active.name
            self.target_tree_name = active.id_data.name
        return context.window_manager.invoke_props_dialog(self, width=250)

    def execute(self, context):
        # Create the tree. ScriptingNodeTree.init() runs and overrides .name,
        # so we set it again after creation. Blender auto-suffixes on collision.
        new_tree = bpy.data.node_groups.new(self.name, "ScriptingNodeTree")
        new_tree.name = self.name
        new_tree.is_group = True

        # Pre-place Group Input + Group Output for a usable starting point
        inp = new_tree.nodes.new("SNA_Node_GroupInput")
        inp.location = (-220, 0)
        out = new_tree.nodes.new("SNA_Node_GroupOutput")
        out.location = (220, 0)

        # Look up the Call Group node we captured at invoke time
        target_node = None
        if self.target_node_name and self.target_tree_name:
            target_tree = bpy.data.node_groups.get(self.target_tree_name)
            if target_tree:
                target_node = target_tree.nodes.get(self.target_node_name)

        if target_node and target_node.bl_idname == "SNA_Node_Group":
            target_node.node_tree = new_tree

        # Switch the editor's path so the user lands inside the new group
        space = context.space_data
        if (
            space
            and space.type == "NODE_EDITOR"
            and hasattr(space, "path")
        ):
            space.path.append(new_tree, node=target_node)

        self.report({"INFO"}, f"Created group '{new_tree.name}'")
        return {"FINISHED"}


class SNA_OT_GoToTree(bpy.types.Operator):
    """Switch the active node editor to a specific tree."""

    bl_idname = "sna.go_to_tree"
    bl_label = "Go To Tree"
    bl_options = {"REGISTER", "UNDO"}

    tree_name: bpy.props.StringProperty()

    def execute(self, context):
        tree = bpy.data.node_groups.get(self.tree_name)
        if not tree:
            self.report({"WARNING"}, f"Tree '{self.tree_name}' not found")
            return {"CANCELLED"}
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type != "NODE_EDITOR":
                    continue
                for space in area.spaces:
                    if space.type == "NODE_EDITOR":
                        space.node_tree = tree
                        return {"FINISHED"}
        return {"FINISHED"}
