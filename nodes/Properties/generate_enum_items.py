import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_GenerateEnumItemsNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GenerateEnumItemsNode"
    bl_label = "Generate Dynamic Enum Items"
    node_color = "PROGRAM"
    bl_width_default = 200
    
    prop_name: bpy.props.StringProperty(name="Enum Property",
                                description="Select the enum property you want to generate items for",
                                update=SN_ScriptingBaseNode._evaluate)

    def on_create(self, context):
        self.add_list_input("Items")

    def evaluate(self, context):
        list_code = "[]"
        from_out = self.inputs[0].from_socket()
        if from_out and from_out.node.bl_idname == "SN_MakeEnumItemNode":
            list_code = f"[{self.inputs[0].python_value}]"
        else:
            list_code = self.inputs[0].python_value
        
        self.code = f"[(item[0], item[1], item[2], item[3], i) for i, item in enumerate({list_code})]"

    def draw_node(self, context, layout):
        layout.prop_search(self, "prop_name", context.scene.sn, "properties", text="")

        if self.prop_name:
            if self.prop_name in context.scene.sn.properties and not context.scene.sn.properties[self.prop_name].property_type == "Enum":
                row = layout.row()
                row.alert = True
                row.label(text="You do not have an enum property selected!", icon="ERROR")
                row = layout.row()
                row.alert = True
                row.label(text="You do not have an enum property selected!", icon="ERROR")
                
            elif not context.scene.sn.properties[self.prop_name].settings.is_dynamic:
                row = layout.row()
                row.alert = True
                row.label(text="The selected property doesn't have dynamic items enabled!", icon="ERROR")
        
        op = layout.operator("node.add_node", text="New Enum Item", icon="ADD")
        op.type = "SN_MakeEnumItemNode"
        op.use_transform = True
        
        from_out = self.inputs[0].from_socket()
        if from_out and from_out.node.bl_idname == "SN_MakeEnumItemNode":
            layout.label(text="Use a list node to combine multiple enum items!", icon="INFO")
        
        if self.prop_name:
            for ref in self.collection.refs:
                node = ref.node
                if node != self and self.prop_name == node.prop_name:
                    row = layout.row()
                    row.alert = True
                    row.label(text="Multiple nodes for this property!", icon="ERROR")