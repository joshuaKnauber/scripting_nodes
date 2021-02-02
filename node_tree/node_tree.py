import bpy
from .. import bl_info
from ..compiler.compiler import compile_addon
from ..settings.updates import exists_newer_version
from uuid import uuid4



def update_create_tree():
    if bpy.context and hasattr(bpy.context,"space_data") and bpy.context.space_data and hasattr(bpy.context.space_data,"node_tree"):
        tree = bpy.context.space_data.node_tree
        if tree and tree.bl_idname == "ScriptingNodesTree":
            if not tree.sn_done_setup:
                bpy.data.node_groups.remove(tree)
                bpy.ops.sn.create_addon("INVOKE_DEFAULT")
            else:
                for group in bpy.data.node_groups:
                    for i, graph in enumerate(group.sn_graphs):
                        if graph.node_tree == tree:
                            bpy.context.scene.sn.editing_addon = group.sn_graphs[0].name
                            group.sn_graph_index = i


class ScriptingNodesTree(bpy.types.NodeTree):

    bl_idname = 'ScriptingNodesTree'
    bl_label = "Visual Scripting"
    bl_icon = 'FILE_SCRIPT'
    
    version: bpy.props.IntVectorProperty(default=(1,1,1))
    
    
    def set_changes(self, value):
        self.has_changes = value
    
    has_changes: bpy.props.BoolProperty(default=True)
    
    def run_autocompile(self):
        addon_tree = bpy.context.scene.sn.addon_tree()
        if addon_tree.sn_graphs[0].autocompile and bpy.context.scene.sn.active_addon_has_changes():
            compile_addon(addon_tree,False)
            if bpy.context.screen:
                for a in bpy.context.screen.areas: a.tag_redraw()
        return addon_tree.sn_graphs[0].autocompile_delay
    

    def setup(self, main_tree):
        self.sn_uid = uuid4().hex[:5].upper()
        
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

        self.sn_version = bl_info["version"]
        self.sn_done_setup = True
        

    def remove_reroutes(self):
        if bpy.context and hasattr(bpy.context,"space_data"):
            if bpy.context.space_data and hasattr(bpy.context.space_data,"node_tree"):
                tree = bpy.context.space_data.node_tree
                if tree:
                    for node in tree.nodes:
                        if node.bl_idname == "NodeReroute":
                            left, right = None, None
                            if node.inputs[0].is_linked and node.outputs[0].is_linked:
                                left = node.inputs[0].links[0].from_socket
                                right = node.outputs[0].links[0].to_socket
                            tree.nodes.remove(node)
                            if left and right:
                                tree.links.new(left, right)
                            

    def do_menu_open(self):
        if bpy.context.preferences.addons[__name__.partition('.')[0]].preferences.use_suggestion_menu:
            region = bpy.context.region
            if region:
                view = region.view2d
                op = bpy.context.active_operator
                if op and hasattr(op,"mouse_x") and hasattr(op,"mouse_y"):
                    view_loc = view.region_to_view(op.mouse_x,op.mouse_y)
                    bpy.ops.sn.run_add_menu("INVOKE_DEFAULT",start_x=view_loc[0],start_y=view_loc[1])


    def update(self):
        self.remove_reroutes()
        self.set_changes(True)
        self.do_menu_open()

        
def upgrade_node_tree(ntree):
    pass
    # print(ntree)
        

def handle_versioning():
    for node_tree in bpy.data.node_groups:
        if node_tree.bl_idname == "ScriptingNodesTree":
            if exists_newer_version(bl_info["version"],node_tree.sn_version):
                upgrade_node_tree(node_tree)