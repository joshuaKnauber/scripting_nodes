"""Tab / Ctrl+Tab to enter/exit node groups in SN editors.

Blender's default keymap binds Tab to `node.group_edit`, but that operator
has built-in poll logic that doesn't always accept custom NodeCustomGroup
subclasses in non-builtin node trees. We bypass it with thin operators that
manipulate the editor's tree path directly.

The path push/pop is exactly what Blender's own navigation does - we just
control the poll ourselves.
"""
import bpy


_addon_keymaps = []


def _in_sn_editor(context):
    """True when the current node editor is showing an SN tree."""
    space = getattr(context, "space_data", None)
    return (
        space is not None
        and space.type == "NODE_EDITOR"
        and getattr(space, "tree_type", None) == "ScriptingNodeTree"
    )


class SNA_OT_GroupEnter(bpy.types.Operator):
    """Push the active node's group onto the editor path."""

    bl_idname = "sna.group_enter"
    bl_label = "Enter Group"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not _in_sn_editor(context):
            return False
        node = getattr(context, "active_node", None)
        if node is None or not getattr(node, "select", False):
            return False
        if not hasattr(node, "node_tree") or node.node_tree is None:
            return False
        # The active node must live in the tree we're currently editing.
        # After tabbing in, the parent tree's active node still leaks via
        # context.active_node - this guards against repeat re-entry.
        space = context.space_data
        if node.id_data is not space.edit_tree:
            return False
        # node.node_tree must REFERENCE a different tree to be enterable.
        # ScriptingBaseNode has a `node_tree` convenience property that
        # returns `self.id_data` (the containing tree), so non-group nodes
        # would otherwise match the hasattr check.
        return node.node_tree is not node.id_data

    def execute(self, context):
        space = context.space_data
        node = context.active_node
        space.path.append(node.node_tree, node=node)
        return {"FINISHED"}


class SNA_OT_GroupExit(bpy.types.Operator):
    """Pop the editor's tree path back to the parent."""

    bl_idname = "sna.group_exit"
    bl_label = "Exit Group"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return _in_sn_editor(context) and len(context.space_data.path) > 1

    def execute(self, context):
        bpy.ops.node.tree_path_parent()
        return {"FINISHED"}


def register():
    kc = bpy.context.window_manager.keyconfigs.addon
    if not kc:
        return

    km = kc.keymaps.new(name="Node Editor", space_type="NODE_EDITOR")

    # Tab: enter the active group node (poll on our op restricts to nodes
    # with a node_tree, so it no-ops when nothing relevant is selected)
    kmi = km.keymap_items.new("sna.group_enter", "TAB", "PRESS")
    _addon_keymaps.append((km, kmi))

    # Ctrl+Tab: exit to the parent tree
    kmi = km.keymap_items.new("sna.group_exit", "TAB", "PRESS", ctrl=True)
    _addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except (RuntimeError, ReferenceError):
            pass
    _addon_keymaps.clear()
