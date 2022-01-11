import bpy
from ..base_node import SN_ScriptingBaseNode



_item_map = dict() # item map to store enum items while debugging. this is moved to generated code for enum props on export

class SN_GenerateEnumItemsNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GenerateEnumItemsNode"
    bl_label = "Generate Dynamic Enum Items"
    node_color = "PROGRAM"
    bl_width_default = 200
    is_trigger = True
    # TODO make template node for things like this where you pick specific property from some source
    

    def on_create(self, context):
        self.add_list_input("Items")
    
    
    prop_name: bpy.props.StringProperty(name="Enum Property",
                                description="Select the enum property you want to generate items for",
                                update=SN_ScriptingBaseNode._evaluate)
    
    prop_source: bpy.props.EnumProperty(name="Property Source",
                                items=[("ADDON", "Addon", "Addon Properties"),
                                        ("NODE", "Node", "Node Properties")],
                                description="Where the property should be selected from",
                                update=SN_ScriptingBaseNode._evaluate)
    
    from_prop_group: bpy.props.BoolProperty(name="Use Property Group",
                                description="Select the property from a property group",
                                update=SN_ScriptingBaseNode._evaluate)
    
    prop_group: bpy.props.StringProperty(name="Property Group",
                                description="Select the property group to select the enum from",
                                update=SN_ScriptingBaseNode._evaluate)
            
            
    def get_enum_source(self):
        """ Returns the parent of the collection the enum property should be searched in """
        sn = bpy.context.scene.sn
        if self.prop_source == "ADDON":
            if self.from_prop_group and self.prop_group in sn.properties and sn.properties[self.prop_group].property_type == "Group":
                return sn.properties[self.prop_group].settings
            elif not self.from_prop_group:
                return sn
        elif self.prop_source == "NODE":
            pass # TODO
        return None
            
            
    def get_prop_group_src(self):
        """ Returns the parent of the collection the property group should be searched in """
        sn = bpy.context.scene.sn
        if self.prop_source == "ADDON":
            return sn
        elif self.prop_source == "NODE":
            pass # TODO
        return None
        
        
    def make_enum_item(self, _id, name, descr, preview_id, uid):
        """ Function for making an enum item while debugging. This is moved to generated code on export in the enum register """
        lookup = f"{str(_id)}\0{str(name)}\0{str(descr)}\0{str(preview_id)}\0{str(uid)}"
        if not lookup in _item_map:
            _item_map[lookup] = (_id, name, descr, preview_id, uid)
        return _item_map[lookup]


    def evaluate(self, context):
        self.code_imperative = ""
        self.code = ""

        enum_src = self.get_enum_source()
        if enum_src and self.prop_name in enum_src.properties and enum_src.properties[self.prop_name].property_type == "Enum":
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
            
            self.code = f"[(item[0], item[1], item[2], item[3], i) for i, item in enumerate({list_code})]"
            # TODO on export use this:
            # self.code = f"[make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate({list_code})]"
    
    
    def draw_warning(self, layout, warning):
        row = layout.row()
        row.alert = True
        row.label(text=warning, icon="ERROR")


    def draw_node(self, context, layout):
        enum_src = self.get_enum_source()
        prop_group_src = self.get_prop_group_src()
        layout.prop(self, "prop_source", text="")
        layout.prop(self, "from_prop_group", text="Use Property Group")
        
        # select prop group and property
        row = layout.row(align=True)
        if self.from_prop_group:
            row.prop_search(self, "prop_group", prop_group_src, "properties", text="", icon="FILEBROWSER")
        if enum_src:
            row.prop_search(self, "prop_name", enum_src, "properties", text="", icon="PRESET")

        # warnings prop group
        if self.from_prop_group and self.prop_group:
            if not self.prop_group in prop_group_src.properties:
                self.draw_warning(layout, "Can't find this property group!")
            elif prop_group_src.properties[self.prop_group].property_type != "Group":
                self.draw_warning(layout, "The selected property is not a group!")

        # warnings enum prop
        if self.prop_name and enum_src:
            if not self.prop_name in enum_src.properties:
                self.draw_warning(layout, "Can't find this enum property!")
            elif enum_src.properties[self.prop_name].property_type != "Enum":
                self.draw_warning(layout, "The selected property is not an enum property!")
            elif not enum_src.properties[self.prop_name].settings.is_dynamic:
                self.draw_warning(layout, "The selected property does not have dynamic items!")
        
        # add item button
        op = layout.operator("node.add_node", text="New Enum Item", icon="ADD")
        op.type = "SN_MakeEnumItemNode"
        op.use_transform = True
        
        # list node info
        from_out = self.inputs[0].from_socket()
        if from_out and from_out.node.bl_idname == "SN_MakeEnumItemNode":
            layout.label(text="Use a list node to combine multiple enum items!", icon="INFO")
        
        # multiple nodes warning
        if self.prop_name:
            for ref in self.collection.refs:
                node = ref.node
                if node != self and self.prop_name == node.prop_name:
                    if self.from_prop_group and node.from_prop_group and self.prop_group == node.prop_group:
                        self.draw_warning(layout, "Multiple nodes found for this property!")
                    elif not self.from_prop_group and not node.from_prop_group:
                        self.draw_warning(layout, "Multiple nodes found for this property!")