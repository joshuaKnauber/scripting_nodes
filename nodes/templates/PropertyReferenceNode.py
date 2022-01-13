import bpy
from ..base_node import SN_ScriptingBaseNode



class PropertyReferenceNode():
    
    prop_name: bpy.props.StringProperty(name="Property",
                                description="Select the property you want to generate items for",
                                update=SN_ScriptingBaseNode._evaluate)
    
    def prop_source_items(self, context):
        items = [("ADDON", "Addon", "Addon Properties"),
                ("NODE", "Node", "Node Properties")]
        return items

    prop_source: bpy.props.EnumProperty(name="Property Source",
                                items=prop_source_items,
                                description="Where the property should be selected from",
                                update=SN_ScriptingBaseNode._evaluate)
    
    from_prop_group: bpy.props.BoolProperty(name="Use Property Group",
                                description="Select the property from a property group",
                                update=SN_ScriptingBaseNode._evaluate)
    
    prop_group: bpy.props.StringProperty(name="Property Group",
                                description="Select the property group to select the property from",
                                update=SN_ScriptingBaseNode._evaluate)
    
    from_node_tree: bpy.props.PointerProperty(type=bpy.types.NodeTree,
                                name="Node Tree", description="Node Tree to select the property node from",
                                poll=lambda _, ntree: ntree.bl_idname == "ScriptingNodesTree",
                                update=SN_ScriptingBaseNode._evaluate)

    from_node: bpy.props.StringProperty(name="Node",
                                description="The node which to take the property from",
                                update=SN_ScriptingBaseNode._evaluate)
    
            
    def get_prop_source(self):
        """ Returns the parent of the collection the property should be searched in """
        if self.prop_source == "ADDON":
            src = bpy.context.scene.sn
        elif self.prop_source == "NODE":
            if self.from_node_tree and self.from_node and self.from_node in self.from_node_tree.nodes:
                src = self.from_node_tree.nodes[self.from_node]
            else:
                return None
        
        if self.from_prop_group and self.prop_group in src.properties and src.properties[self.prop_group].property_type == "Group":
            return src.properties[self.prop_group].settings
        elif not self.from_prop_group:
            return src
        return None
            
            
    def get_prop_group_src(self):
        """ Returns the parent of the collection the property group should be searched in """
        if self.prop_source == "ADDON":
            return bpy.context.scene.sn
        elif self.prop_source == "NODE":
            if self.from_node_tree and self.from_node and self.from_node in self.from_node_tree.nodes:
                return self.from_node_tree.nodes[self.from_node]
        return None
    
    
    def draw_warning(self, layout, warning):
        row = layout.row()
        row.alert = True
        row.label(text=warning, icon="ERROR")
    
    
    def draw_reference_selection(self, layout, unique_selection=False):
        prop_src = self.get_prop_source()
        prop_group_src = self.get_prop_group_src()
        layout.prop(self, "prop_source", text="")
        layout.prop(self, "from_prop_group", text="Use Property Group")

        # select node
        if self.prop_source == "NODE":
            row = layout.row(align=True)
            row.prop_search(self, "from_node_tree", bpy.data, "node_groups", text="")
            if self.from_node_tree:
                row.prop_search(self, "from_node", self.from_node_tree, "nodes", text="")
                if self.from_node in self.from_node_tree.nodes:
                    if not hasattr(self.from_node_tree.nodes[self.from_node], "properties"):
                        self.draw_warning(layout, "The selected node has no properties!")
                elif not self.from_node:
                    self.draw_warning(layout, "No node selected!")
            else:
                self.draw_warning(layout, "No node tree selected!")
            
        
        # select prop group and property
        row = layout.row(align=True)
        if self.from_prop_group:
            row.prop_search(self, "prop_group", prop_group_src, "properties", text="", icon="FILEBROWSER")
        if prop_src:
            row.prop_search(self, "prop_name", prop_src, "properties", text="")

        # warnings prop group
        if self.from_prop_group and self.prop_group:
            if not self.prop_group in prop_group_src.properties:
                self.draw_warning(layout, "Can't find this property group!")
            elif prop_group_src.properties[self.prop_group].property_type != "Group":
                self.draw_warning(layout, "The selected property is not a group!")

        # warnings property
        if self.prop_name and prop_src:
            if not self.prop_name in prop_src.properties:
                self.draw_warning(layout, "Can't find this property!")
        
        # multiple nodes warning
        if unique_selection:
            if self.prop_name:
                for ref in self.collection.refs: # TODO for NODE
                    node = ref.node
                    if node != self and self.prop_name == node.prop_name:
                        if self.from_prop_group and node.from_prop_group and self.prop_group == node.prop_group:
                            self.draw_warning(layout, "Multiple nodes found for this property!")
                        elif not self.from_prop_group and not node.from_prop_group:
                            self.draw_warning(layout, "Multiple nodes found for this property!")