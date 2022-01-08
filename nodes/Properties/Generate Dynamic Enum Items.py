import bpy
from ..base_node import SN_ScriptingBaseNode



_item_map = dict() # item map to store enum items while debugging. this is moved to generated code for enum props on export

class SN_GenerateEnumItemsNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GenerateEnumItemsNode"
    bl_label = "Generate Dynamic Enum Items"
    node_color = "PROGRAM"
    bl_width_default = 200
    is_trigger = True
    
    prop_name: bpy.props.StringProperty(name="Enum Property",
                                description="Select the enum property you want to generate items for",
                                update=SN_ScriptingBaseNode._evaluate)

    def on_create(self, context):
        self.add_list_input("Items")
        
    def make_enum_item(self, _id, name, descr, preview_id, uid):
        """ Function for making an enum item while debugging. This is moved to generated code on export in the enum register """
        lookup = f"{str(_id)}\0{str(name)}\0{str(descr)}\0{str(preview_id)}\0{str(uid)}"
        if not lookup in _item_map:
            _item_map[lookup] = (_id, name, descr, preview_id, uid)
        return _item_map[lookup]

    def evaluate(self, context):
        sn = context.scene.sn
        if self.prop_name in sn.properties and sn.properties[self.prop_name].property_type == "Enum":
            self.code_imperative = f"""
                _item_map = dict()
                def make_enum_item(_id, name, descr, preview_id, uid):
                    lookup = str(_id)+"\\0"+str(name)+"\\0"+str(descr)+"\\0"+str(preview_id)+"\\0"+str(uid)
                    if not lookup in _item_map:
                        _item_map[lookup] = (_id, name, descr, preview_id, uid)
                    return _item_map[lookup]
            """
            
            list_code = "[]"
            from_out = self.inputs[0].from_socket()
            if from_out and from_out.node.bl_idname == "SN_MakeEnumItemNode":
                list_code = f"[{self.inputs[0].python_value}]"
            else:
                list_code = self.inputs[0].python_value
            
            # TODO on export use this:
            # self.code = f"[make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate({list_code})]"
            self.code = f"[(item[0], item[1], item[2], item[3], i) for i, item in enumerate({list_code})]"

        else:
            self.code_imperative = ""
            self.code = ""

    def draw_node(self, context, layout):
        layout.prop_search(self, "prop_name", context.scene.sn, "properties", text="")

        if self.prop_name:
            if self.prop_name in context.scene.sn.properties and not context.scene.sn.properties[self.prop_name].property_type == "Enum":
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