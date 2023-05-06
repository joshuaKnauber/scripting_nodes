import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_OT_MakeSerpensGroup(bpy.types.Operator):
    bl_idname = "sn.make_serpens_group"
    bl_label = "Make Group"
    bl_description = "Make a Serpens node group"
    bl_options = {"REGISTER", "UNDO"}

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

        group = bpy.data.node_groups.new("Node Group", "ScriptingNodesTree")
        group.use_fake_user = True

        input_node = group.nodes.new("SN_NodeGroupInputNode")
        input_node.location = (-200, 0)

        output_node = group.nodes.new("SN_NodeGroupOutputNode")
        output_node.location = (200, 0)

        group.links.new(input_node.outputs[0], output_node.inputs[0])

        node = context.space_data.edit_tree.nodes.new("SN_NodeGroupNode")
        node.group_tree = group
        node.location = center
        context.space_data.edit_tree.nodes.active = node
        return {"FINISHED"}


class SN_OT_EditSerpensGroup(
    bpy.types.Operator
):  # TODO, these ops are blocking other editors
    bl_idname = "sn.edit_serpens_node_group"
    bl_label = "Edit Serpens Group"
    bl_description = "Edit a Serpens node group"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return getattr(context.space_data, "tree_type", None) == "ScriptingNodesTree"

    def execute(self, context):
        path = context.space_data.path
        if hasattr(context.active_node, "group_tree"):
            tree = context.active_node.group_tree
            path.append(tree)
        else:
            path.pop()
        return {"FINISHED"}


class SN_OT_QuitEditSerpensGroup(bpy.types.Operator):
    bl_idname = "sn.quit_edit_serpens_node_group"
    bl_label = "Quit Editing Serpens Group"
    bl_description = "Quit editing a Serpens node group"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return getattr(context.space_data, "tree_type", None) == "ScriptingNodesTree"

    def execute(self, context):
        path = context.space_data.path
        path.pop()
        return {"FINISHED"}


class SN_NodeGroupNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_NodeGroupNode"
    bl_label = "Node Group"
    bl_width_min = 200

    def poll_tree(self, tree):
        return tree.bl_idname == "ScriptingNodesTree"

    group_tree: bpy.props.PointerProperty(type=bpy.types.NodeTree, poll=poll_tree)

    def on_create(self, context):
        print("created")
        self.add_execute_input()
        self.add_execute_output()

    def draw_node(self, context, layout):
        layout.template_ID(self, "group_tree", new="node.new_node_tree")
