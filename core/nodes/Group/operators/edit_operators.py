import bpy

from .....utils.is_serpens import in_sn_tree
from .....core.node_tree.node_tree import ScriptingNodeTree


class SNA_OT_AddGroupNode(bpy.types.Operator):
    bl_idname = "sna.add_group_node"
    bl_label = "Add Group"
    bl_description = "Add this node group"
    bl_options = {"REGISTER", "UNDO"}

    ntree: bpy.props.StringProperty(name="Node Tree", default="")

    def execute(self, context):
        bpy.ops.node.add_node(
            "INVOKE_DEFAULT", type="SNA_NodeGroupNode", use_transform=True
        )
        node = context.active_node
        node.group_tree = bpy.data.node_groups[self.ntree]
        return {"FINISHED"}


class SNA_OT_MakeSerpensGroup(bpy.types.Operator):
    bl_idname = "sna.make_serpens_group"
    bl_label = "Make Group"
    bl_description = "Make a Serpens node group"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return in_sn_tree(context)

    def get_center(self, nodes):
        x = 0
        y = 0
        for node in nodes:
            x += node.location[0]
            y += node.location[1]
        x /= len(nodes)
        y /= len(nodes)
        return (x, y)

    def execute(self, context):
        selected_nodes = context.selected_nodes
        center = self.get_center(selected_nodes)
        # temp
        for node in selected_nodes:
            context.space_data.edit_tree.nodes.remove(node)

        group = bpy.data.node_groups.new("Node Group", ScriptingNodeTree.bl_idname)
        group.use_fake_user = True

        input_node = group.nodes.new("SNA_NodeGroupInputNode")
        input_node.location = (-200, 0)

        output_node = group.nodes.new("SNA_NodeGroupOutputNode")
        output_node.location = (200, 0)

        group.links.new(input_node.outputs[0], output_node.inputs[0])

        node = context.space_data.edit_tree.nodes.new("SNA_NodeGroupNode")
        node.group_tree = group
        node.location = center
        context.space_data.edit_tree.nodes.active = node
        return {"FINISHED"}


class SNA_OT_EditSerpensGroup(bpy.types.Operator):
    bl_idname = "sna.edit_serpens_node_group"
    bl_label = "Edit Serpens Group"
    bl_description = "Edit a Serpens node group"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (
            getattr(context.space_data, "tree_type", None)
            == ScriptingNodeTree.bl_idname
        )

    def execute(self, context):
        path = context.space_data.path
        if hasattr(context.active_node, "group_tree"):
            tree = context.active_node.group_tree
            path.append(tree)
        else:
            path.pop()
        return {"FINISHED"}


class SNA_OT_QuitEditSerpensGroup(bpy.types.Operator):
    bl_idname = "sna.quit_edit_serpens_node_group"
    bl_label = "Quit Editing Serpens Group"
    bl_description = "Quit editing a Serpens node group"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (
            getattr(context.space_data, "tree_type", None)
            == ScriptingNodeTree.bl_idname
        )

    def execute(self, context):
        path = context.space_data.path
        path.pop()
        return {"FINISHED"}
