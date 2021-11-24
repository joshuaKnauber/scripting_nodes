import bpy
from .. import bl_info
from ..compiler.compiler import compile_addon
from ..settings.updates import exists_newer_version
from uuid import uuid4


class ScriptingNodesTree(bpy.types.NodeTree):

    bl_idname = 'ScriptingNodesTree'
    bl_label = "Visual Scripting"
    bl_icon = 'FILE_SCRIPT'

    
    version: bpy.props.IntVectorProperty(default=(1,1,1))
    
    doing_export: bpy.props.BoolProperty(default=False)
    
    
    def set_changes(self, value):
        self.has_changes = value
    
    has_changes: bpy.props.BoolProperty(default=True)
    
    def run_autocompile(self):
        addon_tree = bpy.context.scene.sn.addon_tree()
        if addon_tree:
            if addon_tree.sn_graphs[0].autocompile and bpy.context.scene.sn.active_addon_has_changes():
                compile_addon(addon_tree,False)
                if bpy.context.screen:
                    for a in bpy.context.screen.areas: a.tag_redraw()
            return addon_tree.sn_graphs[0].autocompile_delay
        return None
    

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
                            

    def do_menu_open(self):
        if bpy.context.preferences.addons[__name__.partition('.')[0]].preferences.use_suggestion_menu:
            region = bpy.context.region
            if region:
                view = region.view2d
                op = bpy.context.active_operator
                if op and hasattr(op,"mouse_x") and hasattr(op,"mouse_y"):
                    ui_scale = bpy.context.preferences.system.ui_scale
                    x, y = view.region_to_view(op.mouse_x,op.mouse_y)
                    x, y = x / ui_scale, y / ui_scale
                    bpy.ops.sn.run_add_menu("INVOKE_DEFAULT",start_x=x,start_y=y)


    def update(self):
        self.set_changes(True)
        self.do_menu_open()