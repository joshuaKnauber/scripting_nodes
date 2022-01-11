import bpy
from ...addon.properties.properties import FullBasicProperty



class SN_NodeProperty(FullBasicProperty, bpy.types.PropertyGroup):
    
    @property
    def data_path(self):
        return "" # TODO
    
    def compile(self, context=None):
        self.prop_collection_origin._evaluate(bpy.context)



class PropertyNode():
    
    property_index: bpy.props.IntProperty(name="Index",
                                description="Index of the selected property",
                                min=0, default=0)

    properties: bpy.props.CollectionProperty(type=SN_NodeProperty)
    
    def draw_list(self, layout):
        row = layout.row()
        row.template_list("SN_UL_PropertyList", "", self, "properties", self, "property_index")

        col = row.column(align=True)
        op = col.operator("sn.edit_node_property", text="", icon="GREASEPENCIL")
        op.node_tree = self.node_tree.name
        op.node = self.name
        col.separator()

        op = col.operator("sn.add_node_property", text="", icon="ADD")
        op.node_tree = self.node_tree.name
        op.node = self.name
        op = col.operator("sn.remove_node_property", text="", icon="REMOVE")
        op.node_tree = self.node_tree.name
        op.node = self.name

        col.separator()
        subrow = col.row(align=True)
        subrow.enabled = self.property_index > 0
        op = subrow.operator("sn.move_node_property", text="", icon="TRIA_UP")
        op.node_tree = self.node_tree.name
        op.node = self.name
        op.move_up = True
        subrow = col.row(align=True)
        subrow.enabled = self.property_index < len(self.properties)-1
        op = subrow.operator("sn.move_node_property", text="", icon="TRIA_DOWN")
        op.node_tree = self.node_tree.name
        op.node = self.name
        op.move_up = False