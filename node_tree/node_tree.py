import bpy
from .sockets import get_dynamic_links


def update_create_tree():
    if bpy.context and hasattr(bpy.context,"space_data") and bpy.context.space_data and hasattr(bpy.context.space_data,"node_tree"):
        tree = bpy.context.space_data.node_tree
        if tree and tree.bl_idname == "ScriptingNodesTree" and not tree.done_setup:
            tree.setup(tree)


class ScriptingNodesTree(bpy.types.NodeTree):

    bl_idname = 'ScriptingNodesTree'
    bl_label = "Visual Scripting"
    bl_icon = 'FILE_SCRIPT'
    done_setup: bpy.props.BoolProperty(default=False)


    def setup(self, main_tree):
        graph = main_tree.sn_graphs.add()
        graph.main_tree = main_tree
        graph.node_tree = self

        if main_tree == self:
            graph.name = "New Addon"
            graph.bookmarked = True
        else:
            graph.name = "New Graph"

        main_tree.sn_graph_index = len(main_tree.sn_graphs)-1

        self.done_setup = True


    def update(self):
        for link in get_dynamic_links():
            self.links.remove(link[0])
            self.links.new(link[1],link[2])
        #         from_socket = link.from_socket
        #         to_socket = link.to_socket
        #         self.links.remove(link)
        #         if to_socket.bl_label == "Dynamic":
        #             to_socket_index = int(to_socket.path_from_id().split("[")[-1].replace("]",""))
        #             self.links.new(from_socket,to_socket.node.inputs[to_socket_index-1])
        #         if from_socket.bl_label == "Dynamic":
        #             from_socket_index = int(from_socket.path_from_id().split("[")[-1].replace("]",""))
        #             self.links.new(to_socket,from_socket.node.outputs[from_socket_index-1])