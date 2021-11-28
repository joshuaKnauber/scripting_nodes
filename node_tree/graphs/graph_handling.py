from bpy_extras.io_utils import ImportHelper
import bpy
import os


class SN_OT_RemoveGraph(bpy.types.Operator):
    bl_idname = "sn.remove_graph"
    bl_label = "Remove Graph"
    bl_description = "Removes this graph from the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    index: bpy.props.IntProperty(options={"SKIP_SAVE"})

    def execute(self, context):
        for node in bpy.data.node_groups[self.index].nodes:
            bpy.data.node_groups[self.index].nodes.remove(node)

        bpy.data.node_groups.remove(bpy.data.node_groups[self.index])
        bpy.context.scene.sn.node_tree_index = self.index-1 if self.index>0 else 0
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
            bpy.ops.wm.append(filename=self.graphs, directory=self.path + "\\NodeTree\\")
            #TODO somehow compile new tree

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



