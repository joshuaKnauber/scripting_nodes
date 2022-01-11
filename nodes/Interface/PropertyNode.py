import bpy
from ...addon.properties.properties import FullBasicProperty



class SN_NodeProperty(FullBasicProperty, bpy.types.PropertyGroup):
    
    node_tree_ref: bpy.props.StringProperty(name="Node Tree",
                                    description="Node Tree this property lives in")
    
    node_ref: bpy.props.StringProperty(name="Node",
                                    description="Node this property lives in")

    @property
    def node(self):
        if self.node_tree_ref and self.node_ref:
            return bpy.data.node_groups[self.node_tree_ref].nodes[self.node_ref]
        return None
    
    @property
    def data_path(self):
        return "" # TODO



class PropertyNode():
    
    prop_index: bpy.props.IntProperty(name="Index",
                                description="Index of the selected property",
                                min=0, default=0)

    properties: bpy.props.CollectionProperty(type=SN_NodeProperty)
    
    def draw_list(self, layout):
        row = layout.row()
        row.template_list("SN_UL_PropertyList", "", self, "properties", self, "prop_index")

        col = row.column(align=True)
        op = col.operator("sn.add_node_property", text="", icon="ADD")
        op.node_tree = self.node_tree.name
        op.node = self.name
        op = col.operator("sn.remove_node_property", text="", icon="REMOVE")
        op.node_tree = self.node_tree.name
        op.node = self.name
        col.separator()
        op = col.operator("sn.edit_node_property", text="", icon="GREASEPENCIL")
        op.node_tree = self.node_tree.name
        op.node = self.name