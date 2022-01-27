import bpy
from ..base_node import SN_ScriptingBaseNode



class PropertyReferenceNode():
    
    allow_prop_paste = False
    add_indexing_inputs = False


    def _disect_data_path(self, path):
        # remove assign part
        path = path.split("=")[0]
        path = path.strip()
        # replace escaped quotes
        path = path.replace('\\"', '"')
        # split data path in segments
        segments = []
        for segment in path.split(".")[1:]:
            if segments and "[" in segments[-1] and not "]" in segments[-1]:
                segments[-1] += f".{segment}"
            else:
                segments.append(segment)
        # remove indexing from property name
        segments[-1] = segments[-1].split("[")[0]
        return segments
    
    def _is_valid_data_path(self, path):
        return path and "bpy." in path and not ".ops." in path

    def get_data(self):
        if self._is_valid_data_path(self.pasted_data_path):
            return self._disect_data_path(self.pasted_data_path)
        return None
    
    
    def segment_is_indexable(self, segment):
        """ Returns if a segment can be indexed. A segment is a string part of a data path """
        return "[" in segment and "]" in segment
    
    def create_inputs_from_path(self):
        """ Creates the inputs for the given data path """
        self.inputs.clear()
        data = self.get_data()
        if data:
            for segment in data:
                if self.segment_is_indexable(segment):
                    name = segment.split("[")[0].replace("_", " ").title()
                    if name[-1] == "s": name = name[:-1]
                    if '"' in segment or "'" in segment:
                        inp = self.add_string_input(name)
                        inp["default_value"] = segment.split("[")[-1].split("]")[0][1:-1]
                        inp.index_type = "String"
                    else:
                        inp = self.add_integer_input(name)
                        inp["default_value"] = int(segment.split("[")[-1].split("]")[0])
                        inp.index_type = "Integer"
                    inp.indexable = True
                    
    def get_pasted_prop_name(self):
        if self.pasted_data_path:
            return self.pasted_data_path.split(".")[-1].replace("_", " ").split("[")[0].title()
        return "Property"
    
    
    def on_prop_change(self, context):
        if self.add_indexing_inputs:
            if self.prop_source == "BLENDER":
                self.label = self.get_pasted_prop_name()
                self.create_inputs_from_path()
            else:
                prop_src = self.get_prop_source()
                self.inputs[0].name = "Data"
                self.label = "Custom Property"
                if self.prop_name and prop_src:
                    if self.prop_name in prop_src.properties:
                        prop = prop_src.properties[self.prop_name]
                        self.label = prop.name
                        # property from group -> input is pointer
                        if self.from_prop_group:
                            self.inputs[0].name = "Pointer Property"
                        # addon property
                        elif hasattr(prop, "attach_to"):
                            self.inputs[0].name = prop.attach_to
                        # node property
                        else:
                            self.inputs[0].name = prop_src.bl_label
        self._evaluate(context)
    
    
    prop_name: bpy.props.StringProperty(name="Property",
                                description="Select the property you want to generate items for",
                                update=on_prop_change)

    
    def prop_source_items(self, context):
        items = [("ADDON", "Addon", "Addon Properties"),
                ("NODE", "Node", "Node Properties")]
        if self.allow_prop_paste:
            items.append(("BLENDER", "Blender", "Blender"))
        return items

    prop_source: bpy.props.EnumProperty(name="Property Source",
                                items=prop_source_items,
                                description="Where the property should be selected from",
                                update=on_prop_change)
    
    from_prop_group: bpy.props.BoolProperty(name="Use Property Group",
                                description="Select the property from a property group",
                                update=on_prop_change)
    
    prop_group: bpy.props.StringProperty(name="Property Group",
                                description="Select the property group to select the property from",
                                update=on_prop_change)
    
    from_node_tree: bpy.props.PointerProperty(type=bpy.types.NodeTree,
                                name="Node Tree", description="Node Tree to select the property node from",
                                poll=lambda _, ntree: ntree.bl_idname == "ScriptingNodesTree",
                                update=on_prop_change)

    from_node: bpy.props.StringProperty(name="Node",
                                description="The node which to take the property from",
                                update=on_prop_change)
    
    pasted_data_path: bpy.props.StringProperty(name="Pasted Path",
                                description="The full data path to the property",
                                update=on_prop_change)
    
            
    def get_prop_source(self):
        """ Returns the parent of the collection the property should be searched in """
        if self.prop_source == "ADDON":
            src = bpy.context.scene.sn
        elif self.prop_source == "NODE":
            if self.from_node_tree and self.from_node and self.from_node in self.from_node_tree.nodes:
                src = self.from_node_tree.nodes[self.from_node]
            else:
                return None
        
        if self.from_prop_group and hasattr(src, "properties") and self.prop_group in src.properties and src.properties[self.prop_group].property_type == "Group":
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
                node = self.from_node_tree.nodes[self.from_node]
                if hasattr(node, "properties"):
                    return node
        return None
    
    
    def draw_warning(self, layout, warning):
        row = layout.row()
        row.alert = True
        row.label(text=warning, icon="ERROR")
    
    
    def draw_reference_selection(self, layout, unique_selection=False, draw_prop_source=True):
        if draw_prop_source:
            layout.prop(self, "prop_source", expand=True)

        if self.prop_source == "BLENDER":
            row = layout.row(align=True)
            row.scale_y = 1.5
            op = row.operator("sn.paste_data_path", text=self.get_pasted_prop_name() if self.pasted_data_path else "Paste Property", icon="PASTEDOWN")
            op.node = self.name
            op.node_tree = self.node_tree.name
            if self.pasted_data_path:
                op = row.operator("sn.reset_data_path", text="", icon="LOOP_BACK")
                op.node = self.name
                op.node_tree = self.node_tree.name
        
        else:
            layout.prop(self, "from_prop_group", text="From Property Group")
            prop_src = self.get_prop_source()
            prop_group_src = self.get_prop_group_src()

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
            if self.from_prop_group and prop_group_src:
                row.prop_search(self, "prop_group", prop_group_src, "properties", text="", icon="FILEBROWSER")
            if prop_group_src and prop_src:
                row.prop_search(self, "prop_name", prop_src, "properties", text="")

            # warnings prop group
            if self.from_prop_group and self.prop_group and prop_group_src:
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
                    for node in self.collection.nodes: # TODO for NODE
                        if node != self and self.prop_source == node.prop_source and self.prop_name == node.prop_name:
                            if self.prop_source == "ADDON" or (self.prop_source == "NODE" and self.from_node == node.from_node and self.from_node_tree == self.from_node_tree):
                                if self.from_prop_group and node.from_prop_group and self.prop_group == node.prop_group:
                                    self.draw_warning(layout, "Multiple nodes found for this property!")
                                    break
                                elif not self.from_prop_group and not node.from_prop_group:
                                    self.draw_warning(layout, "Multiple nodes found for this property!")
                                    break