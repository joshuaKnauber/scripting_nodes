import bpy
from .sockets import get_dynamic_links, get_remove_links


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
        graph.blender = bpy.app.version

        if main_tree == self:
            graph.name = "New Addon"
            graph.bookmarked = True
        else:
            graph.name = "New Graph"

        main_tree.sn_graph_index = len(main_tree.sn_graphs)-1

        self.done_setup = True
        
        
    def update_dynamic_links(self):
        dynamic_links = get_dynamic_links()
        for link in dynamic_links:
            self.links.remove(link[0])
            self.links.new(link[1],link[2])
        dynamic_links.clear()
        
        
    def update_remove_links(self):
        remove_links = get_remove_links()
        for link in remove_links:
            self.links.remove(link)
        remove_links.clear()


    def update(self):
        self.update_dynamic_links()
        self.update_remove_links()