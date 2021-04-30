import bpy
import os
import getpass
from bpy_extras.io_utils import ImportHelper



class SN_OT_CreateAddon(bpy.types.Operator):
    bl_idname = "sn.create_addon"
    bl_label = "Create Addon"
    bl_description = "Adds a new addon to this file"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    bl_property = "name"
    
    name: bpy.props.StringProperty(name="Name",
                                   description="Name of the new addon you are creating",
                                   default="New Addon")

    author: bpy.props.StringProperty(name="Author",
                                     description="The name of the addons author",
                                     default="Your Name")

    def execute(self, context):
        tree = bpy.data.node_groups.new(self.name, "ScriptingNodesTree")
        tree.setup(tree)
        tree.sn_graphs[0].name = self.name
        tree.sn_graphs[0].author = self.author
        context.scene.sn.editing_addon = self.name
        return {"FINISHED"}
    
    def draw(self,context):
        self.layout.prop(self,"name",text="Name")
        self.layout.prop(self,"author",text="Author")

    def invoke(self, context, event):
        try:
            user = getpass.getuser()
        except:
            user = ""
        self.author = user
        return context.window_manager.invoke_props_dialog(self)



class SN_OT_DeleteAddon(bpy.types.Operator):
    bl_idname = "sn.delete_addon"
    bl_label = "Delete this addon?"
    bl_description = "This will delete the active addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        graphs = context.scene.sn.addon_tree().sn_graphs
        for index in range(len(graphs)-1,0,-1):
            bpy.data.node_groups.remove(graphs[index].node_tree)
        bpy.data.node_groups.remove(context.scene.sn.addon_tree())
        if context.scene.sn.addon_tree():
            context.space_data.node_tree = context.scene.sn.addon_tree()
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self,event)



class SN_OT_CreateGraph(bpy.types.Operator):
    bl_idname = "sn.add_graph"
    bl_label = "Add Graph"
    bl_description = "Adds a new graph to this addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}


    def execute(self, context):
        tree = bpy.data.node_groups.new("New Graph", "ScriptingNodesTree")
        addon_tree = context.scene.sn.addon_tree()
        tree.setup(addon_tree)
        return {"FINISHED"}



class SN_OT_MoveGraph(bpy.types.Operator):
    bl_idname = "sn.move_graph"
    bl_label = "Move Graph"
    bl_description = "Moves this graph"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    up: bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        addon_tree = context.scene.sn.addon_tree()
        return addon_tree.sn_graph_index != 0

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        if (self.up):
            addon_tree.sn_graphs.move(addon_tree.sn_graph_index,addon_tree.sn_graph_index-1)
            addon_tree.sn_graph_index -= 1
        else:
            addon_tree.sn_graphs.move(addon_tree.sn_graph_index,addon_tree.sn_graph_index+1)
            addon_tree.sn_graph_index += 1
        return {"FINISHED"}
    


class SN_OT_RemoveGraph(bpy.types.Operator):
    bl_idname = "sn.remove_graph"
    bl_label = "Remove Graph"
    bl_description = "Removes this graph from the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    index: bpy.props.IntProperty(options={"SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        addon_tree = context.scene.sn.addon_tree()
        return addon_tree.sn_graph_index != 0

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        for node in addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree.nodes:
            addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree.nodes.remove(node)

        bpy.data.node_groups.remove(addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree)
        addon_tree.sn_graphs.remove(addon_tree.sn_graph_index)
        addon_tree.sn_graph_index -= 1
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    

class SN_OT_AppendPopup(bpy.types.Operator):
    bl_idname = "sn.append_popup"
    bl_label = "Append Graph"
    bl_description = "Appends this graph from the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    def get_graph_items(self,context):
        items = []
        with bpy.data.libraries.load(self.path) as (data_from, data_to):
            for group in data_from.node_groups:
                items.append((group,group,group))
        if not items:
            items = [("NONE","NONE","NONE")]
        return items

    path: bpy.props.StringProperty()
    graphs: bpy.props.EnumProperty(name="Graph",
                                   description="Graph to import",
                                   items=get_graph_items)

    def execute(self, context):
        if self.graphs != "NONE":
            addon_tree = context.scene.sn.addon_tree()

            if self.graphs in bpy.data.node_groups:
                bpy.data.node_groups[self.graphs].name += "_1"

            old_trees = list(bpy.data.node_groups)
            with bpy.data.libraries.load(self.path) as (data_from, data_to):
                data_to.node_groups = [self.graphs]

            keep_tree = None
            for tree in bpy.data.node_groups:
                if not tree in old_trees:
                    if not tree.name == self.graphs:
                        bpy.data.node_groups.remove(tree)
                    else:
                        keep_tree = tree

            if keep_tree:
                keep_tree.setup(addon_tree)
            
        return {"FINISHED"}
    
    def draw(self,context):
        if self.graphs == "NONE":
            self.layout.label(text="No Graphs found in this blend file",icon="ERROR")
        else:
            self.layout.prop(self,"graphs",text="Graph")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    
    
class SN_OT_AppendGraph(bpy.types.Operator, ImportHelper):
    bl_idname = "sn.append_graph"
    bl_label = "Append Graph"
    bl_description = "Appends a graph from another file to this addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    filter_glob: bpy.props.StringProperty( default='*.blend', options={'HIDDEN'} )

    def execute(self, context):
        filename, extension = os.path.splitext(self.filepath)
        if extension == ".blend":
            bpy.ops.sn.append_popup("INVOKE_DEFAULT",path=self.filepath)
        return {"FINISHED"}