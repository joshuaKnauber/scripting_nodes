import bpy
from .sockets.base_sockets import get_dynamic_links, get_remove_links
from ..compiler.compiler import compile_addon


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
    
    
    def set_changes(self, value):
        self.has_changes = value
    
    has_changes: bpy.props.BoolProperty(default=True)
    
    def run_autocompile(self):
        addon_tree = bpy.context.scene.sn.addon_tree()
        if addon_tree.sn_graphs[0].autocompile and bpy.context.scene.sn.active_addon_has_changes():
            compile_addon(addon_tree)
            if bpy.context.screen:
                for a in bpy.context.screen.areas: a.tag_redraw()
        return addon_tree.sn_graphs[0].autocompile_delay
    

    def setup(self, main_tree):
        graph = main_tree.sn_graphs.add()
        graph.main_tree = main_tree
        graph.node_tree = self
        graph.blender = bpy.app.version

        if main_tree == self:
            bpy.app.timers.register(self.run_autocompile, first_interval=0.1)
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
            link = self.links.new(link[1],link[2])
            link.from_node.insert_link(link)
            link.to_node.insert_link(link)
        dynamic_links.clear()
        
        
    def update_remove_links(self):
        remove_links = get_remove_links()
        for link in remove_links:
            try:
                self.links.remove(link)
            except:
                pass
        remove_links.clear()


    def update(self):
        self.set_changes(True)
        self.update_dynamic_links()
        self.update_remove_links()