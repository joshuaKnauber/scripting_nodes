import bpy
import re
from ..base_node import SN_ScriptingBaseNode


def update_graph_index(self, context):
    graph_tree = self.sn_graphs[self.sn_graph_index].node_tree
    context.space_data.node_tree = graph_tree
    context.scene.sn.bookmarks = self.sn_graphs[self.sn_graph_index].name



def name_is_unique(collection, name):
    count = 0
    for item in collection:
        if item.name == name:
            count += 1
    return count <= 1

def get_unique_name(collection, base_name):
    if name_is_unique(collection, base_name):
        return base_name
    else:
        max_num = 0
        if "." in base_name and base_name.split(".")[-1].isnumeric():
            base_name = (".").join(base_name.split(".")[:-1])
        for item in collection:
            if "." in item.name and item.name.split(".")[-1].isnumeric():
                item_base_name = (".").join(item.name.split(".")[:-1])
                if item_base_name == base_name:
                    max_num = max(max_num, int(item.name.split(".")[-1]))
        return base_name + "." + str(max_num+1).zfill(3)
    
    
    
class SN_Error(bpy.types.PropertyGroup):
    
    title: bpy.props.StringProperty()
    description: bpy.props.StringProperty()
    fatal: bpy.props.BoolProperty()
    node: bpy.props.StringProperty()
    node_tree: bpy.props.StringProperty()
    
    
    
class SN_Print(bpy.types.PropertyGroup):
    
    value: bpy.props.StringProperty()
    


class SN_Graph(bpy.types.PropertyGroup):
    
    def short(self):
        return re.sub(r'\W+', '', self.name.replace(" ","_")).lower()

    def get_python_name(self, name, empty_name=""):
        return SN_ScriptingBaseNode().get_python_name(name, empty_name)
    
    def update_autocompile(self,context):
        self.main_tree.set_changes(True)
    
    autocompile: bpy.props.BoolProperty(default=False,
                                        name="Auto Compile",
                                        description="Automatically compiles your node tree when you make changes",
                                        update=update_autocompile)
    
    autocompile_delay: bpy.props.FloatProperty(default=2,
                                               min=0.5,
                                               soft_max=5,
                                               name="Auto Compile Delay",
                                               description="The time waited before trying to automatically compile in seconds")
    
    compile_on_start: bpy.props.BoolProperty(default=False,
                                             name="Compile on Startup",
                                             description="Compiles this addon when you open this blender scene")
    
    errors: bpy.props.CollectionProperty(type=SN_Error)

    prints: bpy.props.CollectionProperty(type=SN_Print)
    
    last_compile_time: bpy.props.StringProperty(default="0s",
                                               name="Last Time",
                                               description="The time the last compile took")

    bookmarked: bpy.props.BoolProperty(default=False,
                                        name="Bookmark",
                                        description="Will show this graph in the header for quick access")



class SN_UL_GraphList(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(icon="FILE_SCRIPT")
        row.prop(item, "name", emboss=False, text="")

    def filter_items(self, context, data, propname):
        node_trees = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list

        flt_flags = helper_funcs.filter_items_by_name("ScriptingNodesTree", self.bitflag_filter_item, node_trees, "bl_idname", reverse=False)
        flt_neworder = helper_funcs.sort_items_by_name(node_trees, "name")

        return flt_flags, flt_neworder