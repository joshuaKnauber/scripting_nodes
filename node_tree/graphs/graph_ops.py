from bpy_extras.io_utils import ImportHelper
import bpy
import os
from .node_tree import compile_all, unregister_all



def get_serpens_graphs():
    graphs = []
    for group in bpy.data.node_groups:
        if group.bl_idname == "ScriptingNodesTree":
            graphs.append(group)
    return graphs



class SN_OT_AddGraph(bpy.types.Operator):
    bl_idname = "sn.add_graph"
    bl_label = "Add Node Tree"
    bl_description = "Adds a node tree to the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        sn = context.scene.sn
        graph = bpy.data.node_groups.new("NodeTree", "ScriptingNodesTree")
        for index, group in enumerate(bpy.data.node_groups):
            if group == graph:
                sn.node_tree_index = index
        return {"FINISHED"}



class SN_OT_RemoveGraph(bpy.types.Operator):
    bl_idname = "sn.remove_graph"
    bl_label = "Remove Node Tree"
    bl_description = "Removes this node tree from the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        if context.scene.sn.node_tree_index < len(bpy.data.node_groups):
            return bpy.data.node_groups[context.scene.sn.node_tree_index].bl_idname == "ScriptingNodesTree"

    def execute(self, context):
        sn = context.scene.sn
        group = bpy.data.node_groups[sn.node_tree_index]
        group.graph_unregister()
        bpy.data.node_groups.remove(group)
        sn.node_tree_index -= 1
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    
    
class SN_OT_AppendGraph(bpy.types.Operator, ImportHelper):
    bl_idname = "sn.append_graph"
    bl_label = "Append Node Tree"
    bl_description = "Appends a node tree from another file to this addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    filter_glob: bpy.props.StringProperty( default='*.blend', options={'HIDDEN'} )

    def execute(self, context):
        _, extension = os.path.splitext(self.filepath)
        if extension == ".blend":
            bpy.ops.sn.append_popup("INVOKE_DEFAULT", path=self.filepath)
        return {"FINISHED"}



class SN_OT_AppendPopup(bpy.types.Operator):
    bl_idname = "sn.append_popup"
    bl_label = "Append Node Tree"
    bl_description = "Appends this node tree from the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def get_graph_items(self, context):
        """ Returns all node trees that can be found in the selected file """
        items = []
        with bpy.data.libraries.load(self.path) as (data_from, _):
            for group in data_from.node_groups:
                items.append((group, group, group))
        if not items:
            items = [("NONE", "NONE", "NONE")]
        return items

    path: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    graph: bpy.props.EnumProperty(name="Node Tree",
                                   description="Node Tree to import",
                                   items=get_graph_items,
                                   options={"HIDDEN", "SKIP_SAVE"})

    def execute(self, context):
        if self.graph != "NONE":
            # save previous groups
            prev_groups = bpy.data.node_groups.values()

            # append node group
            with bpy.data.libraries.load(self.path) as (_, data_to):
                data_to.node_groups = [self.graph]
            
            # register new graph
            new_groups = set(prev_groups) ^ set(bpy.data.node_groups.values())
            for group in new_groups:
                group.compile(hard=True)
                context.scene.sn.node_tree_index = bpy.data.node_groups.values().index(group)
            
            # redraw screen
            context.area.tag_redraw()
        return {"FINISHED"}
    
    def draw(self, context):
        if self.graph == "NONE":
            self.layout.label(text="No Node Trees found in this blend file",icon="ERROR")
        else:
            self.layout.prop(self, "graph", text="Node Tree")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)



class SN_OT_ForceCompile(bpy.types.Operator):
    bl_idname = "sn.force_compile"
    bl_label = "This might be slow for large addons!"
    bl_description = "Forces all node trees to compile"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        unregister_all()
        compile_all(hard=True)
        
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                for refs in ntree.node_refs:
                    refs.clear_unused_refs()
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)



class SN_OT_ForceUnregister(bpy.types.Operator):
    bl_idname = "sn.force_unregister"
    bl_label = "Force Unregister"
    bl_description = "Forces all node trees to unregister"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        unregister_all()
        return {"FINISHED"}