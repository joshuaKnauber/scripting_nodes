import bpy


def update_graph_index(self, context):
    context.space_data.node_tree = self.sn_graphs[self.sn_graph_index].node_tree


class SN_GraphItem(bpy.types.PropertyGroup):

    def update_name(self,context):
        self.node_tree.name = self.name

    node_tree: bpy.props.PointerProperty(type=bpy.types.NodeTree)

    addon_tree: bpy.props.PointerProperty(type=bpy.types.NodeTree)
    
    name: bpy.props.StringProperty(name="Name", description="The name of this graph", default="My Graph", update=update_name)

    graph_type: bpy.props.EnumProperty(items=[("GRAPH","Graph","Graph"),("FUNCTION","Function","Function")], default="GRAPH")

    is_main_graph: bpy.props.BoolProperty(default=False)


class SN_UL_GraphList(bpy.types.UIList):

    def get_graph_icon(self,item):
        if item.graph_type == "GRAPH":
            if item.is_main_graph:
                return "FILE_SCRIPT"
            return "SCRIPTPLUGINS"
        else:
            if item.is_main_graph:
                return "SCRIPTPLUGINS"
            return "DRIVER_TRANSFORM"
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", icon=self.get_graph_icon(item), text="")