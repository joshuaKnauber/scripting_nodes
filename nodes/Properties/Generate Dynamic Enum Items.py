import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyReferenceNode import PropertyReferenceNode



_item_map = dict() # item map to store enum items while debugging. this is moved to generated code for enum props on export


class SN_GenerateEnumItemsNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyReferenceNode):

    bl_idname = "SN_GenerateEnumItemsNode"
    bl_label = "Generate Dynamic Enum Items"
    node_color = "PROGRAM"
    bl_width_default = 250
    is_trigger = True
    
    
    enum_item_funcs = {}
    

    def on_create(self, context):
        self.add_list_input("Items")
        
        
    def make_enum_item(self, _id, name, descr, preview_id, uid):
        """ Function for making an enum item while debugging. This is moved to generated code on export in the enum register """
        lookup = f"{str(_id)}\0{str(name)}\0{str(descr)}\0{str(preview_id)}\0{str(uid)}"
        if not lookup in _item_map:
            _item_map[lookup] = (_id, name, descr, preview_id, uid)
        return _item_map[lookup]


    def evaluate(self, context):
        # self.code_imperative = ""
        # self.code = ""
        
        enum_src = self.get_prop_source()
        if enum_src and self.prop_name in enum_src.properties and enum_src.properties[self.prop_name].property_type == "Enum":
            prop = enum_src.properties[self.prop_name]
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
            
            enum_item_func_name = f"items_{prop.python_name}_{self.static_uid}"
            self.code = f"""
                        # this code doesn't reflect how you would usually write this
                        def {enum_item_func_name}(self, context):
                            return [make_enum_item(item[0], item[1], item[2], item[3], {'2**i' if prop.settings.enum_flag else 'i'}) for i, item in enumerate({list_code})]

                        node = bpy.data.node_groups['{self.node_tree.name}'].nodes['{self.name}']
                        node.enum_item_funcs['{self.as_pointer()}'] = {enum_item_func_name}
                        """
            # TODO export


    def draw_node(self, context, layout):
        self.draw_reference_selection(layout, True)
        prop_src = self.get_prop_source()
        if self.prop_name and prop_src and self.prop_name in prop_src.properties:
            if prop_src.properties[self.prop_name].property_type != "Enum":
                self.draw_warning(layout, "The selected property is not an enum property!")
            elif not prop_src.properties[self.prop_name].settings.is_dynamic:
                self.draw_warning(layout, "The selected property does not have dynamic items!")
        
        # add item button
        op = layout.operator("node.add_node", text="New Enum Item", icon="ADD")
        op.type = "SN_MakeEnumItemNode"
        op.use_transform = True
        
        # list node info
        from_out = self.inputs[0].from_socket()
        if from_out and from_out.node.bl_idname == "SN_MakeEnumItemNode":
            layout.label(text="Use a list node to combine multiple enum items!", icon="INFO")