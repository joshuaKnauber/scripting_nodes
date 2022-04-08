import bpy
from ..base_node import SN_ScriptingBaseNode



class StringMap(bpy.types.PropertyGroup):

    def update_item(self, context):
        for node in self.id_data.node_collection("SN_MapStringsNode").nodes:
            for item in node.map_collection:
                if item == self:
                    node._evaluate(context)
                    return
    
    name: bpy.props.StringProperty(name="From", description="The value from which to map", update=update_item)
    to_string: bpy.props.StringProperty(name="To", description="The value to which to map", update=update_item)



class SN_MapStringsNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_MapStringsNode"
    bl_label = "Map Strings"
    node_color = "STRING"
    bl_width_default = 200

    def on_create(self, context):
        self.add_string_input("Input")
        self.add_string_output("Mapped")
        
    map_collection: bpy.props.CollectionProperty(type=StringMap)

    def evaluate(self, context):
        lookup = "{"
        for item in self.map_collection:
            lookup += f"'{item.name}': '{item.to_string}', "
        lookup += "}"
        self.outputs[0].python_value = f"{lookup}[{self.inputs[0].python_value}]"
    
    def draw_node(self, context, layout):
        op = layout.operator("sn.add_string_map_item", icon="ADD")
        op.node_tree = self.node_tree.name
        op.node = self.name

        col = layout.column(align=True)
        for i, item in enumerate(self.map_collection):
            box = col.box()
            row = box.row()
            row.prop(item, "name")
            op = row.operator("sn.remove_string_map_item", text="", icon="PANEL_CLOSE", emboss=False)
            op.node_tree = self.node_tree.name
            op.node = self.name
            op.index = i
            box.prop(item, "to_string")