import bpy
from ...base_node import SN_ScriptingBaseNode
from ...templates.PropertyReferenceNode import PropertyReferenceNode
from ....utils import collection_has_item, collection_get_item



class SN_GenerateEnumItemsNode(SN_ScriptingBaseNode, bpy.types.Node, PropertyReferenceNode):

    bl_idname = "SN_GenerateEnumItemsNode"
    bl_label = "Generate Dynamic Enum Items"
    node_color = "PROGRAM"
    bl_width_default = 240
    is_trigger = True
        

    def on_create(self, context):
        self.add_list_input("Items")
        

    def evaluate(self, context):        
        enum_src = self.get_prop_source()
        prop = collection_get_item(enum_src.properties, self.prop_name) if enum_src else None
        if prop and prop.property_type == "Enum":
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
            
            self.code = f"""
                def {prop.settings.item_func_name}(self, context):
                    enum_items = {list_code}
                    return [make_enum_item(item[0], item[1], item[2], item[3], {'2**i' if prop.settings.enum_flag else 'i'}) for i, item in enumerate(enum_items)]
                """


    def draw_node(self, context, layout):
        self.draw_reference_selection(layout, True)
        prop_src = self.get_prop_source()
        prop = collection_get_item(prop_src.properties, self.prop_name) if (self.prop_name and prop_src) else None
        if prop:
            if prop.property_type != "Enum":
                self.draw_warning(layout, "The selected property is not an enum property!")
            elif not prop.settings.is_dynamic:
                self.draw_warning(layout, "The selected property does not have dynamic items!")
        
        # add item button
        op = layout.operator("node.add_node", text="New Enum Item", icon="ADD")
        op.type = "SN_MakeEnumItemNode"
        op.use_transform = True
        
        # list node info
        from_out = self.inputs[0].from_socket()
        if from_out and from_out.node.bl_idname == "SN_MakeEnumItemNode":
            layout.label(text="Use a list node to combine multiple enum items!", icon="INFO")