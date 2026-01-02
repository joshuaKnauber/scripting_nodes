import bpy
from ....lib.utils.node_tree.scripting_node_trees import node_by_id


def go_to_node(context, node):
    """Navigate to a specific node in a node tree"""
    if not node:
        return False

    # Get the node tree from the node
    ntree = node.id_data

    # Find the Node Editor area and use context override
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "NODE_EDITOR":
                # Set the node tree
                for space in area.spaces:
                    if space.type == "NODE_EDITOR":
                        space.node_tree = ntree
                        break

                # Deselect all nodes and select the target node
                for n in ntree.nodes:
                    n.select = False
                node.select = True
                ntree.nodes.active = node

                # Frame the view on the node with context override
                for region in area.regions:
                    if region.type == "WINDOW":
                        with context.temp_override(
                            window=window, area=area, region=region
                        ):
                            bpy.ops.node.view_selected()
                        return True
    return False


class SNA_OT_GoToNode(bpy.types.Operator):
    """Navigate to a specific node in a node tree"""

    bl_idname = "sna.go_to_node"
    bl_label = "Go To Node"
    bl_options = {"REGISTER", "UNDO"}

    node_id: bpy.props.StringProperty()

    def execute(self, context):
        node = node_by_id(self.node_id)
        if not node:
            self.report({"WARNING"}, "Node not found")
            return {"CANCELLED"}

        go_to_node(context, node)
        return {"FINISHED"}
