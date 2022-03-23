import bpy
from ...nodes.compiler import compile_addon



class SN_OT_AddProperty(bpy.types.Operator):
    bl_idname = "sn.add_property"
    bl_label = "Add Property"
    bl_description = "Adds a property to the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        sn = context.scene.sn
        new_prop = sn.properties.add()
        new_prop.name = "New Property"
        for index, property in enumerate(sn.properties):
            if property == new_prop:
                sn.property_index = index
        return {"FINISHED"}



class SN_OT_RemoveProperty(bpy.types.Operator):
    bl_idname = "sn.remove_property"
    bl_label = "Remove Property"
    bl_description = "Removes this property from the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        return context.scene.sn.property_index < len(context.scene.sn.properties)

    def execute(self, context):
        sn = context.scene.sn
        sn.properties.remove(sn.property_index)
        sn.property_index -= 1
        compile_addon()
        return {"FINISHED"}



class SN_OT_RemoveGroupProperty(bpy.types.Operator):
    bl_idname = "sn.remove_group_property"
    bl_label = "Remove Property"
    bl_description = "Removes this property from the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    group_items_path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    index: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        items = eval(self.group_items_path)
        items.remove(self.index)
        return {"FINISHED"}



class SN_OT_MoveProperty(bpy.types.Operator):
    bl_idname = "sn.move_property"
    bl_label = "Move Property"
    bl_description = "Moves this property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    move_up: bpy.props.BoolProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        sn = context.scene.sn
        if self.move_up:
            sn.properties.move(sn.property_index, sn.property_index - 1)
            sn.property_index -= 1
        else:
            sn.properties.move(sn.property_index, sn.property_index + 1)
            sn.property_index += 1
        return {"FINISHED"}



class SN_OT_MoveGroupProperty(bpy.types.Operator):
    bl_idname = "sn.move_group_property"
    bl_label = "Move Property"
    bl_description = "Moves this property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    group_items_path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    index: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})
    move_up: bpy.props.BoolProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        items = eval(self.group_items_path)
        if self.move_up:
            items.move(self.index, self.index - 1)
        else:
            items.move(self.index, self.index + 1)
        return {"FINISHED"}



class SN_OT_CopyPythonName(bpy.types.Operator):
    bl_idname = "sn.copy_python_name"
    bl_label = "Copy Python Name"
    bl_description = "Copies the python name of this item to use in scripts"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    name: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        context.window_manager.clipboard = self.name
        self.report({"INFO"}, message="Copied!")
        return {"FINISHED"}



class SN_OT_AddEnumItem(bpy.types.Operator):
    bl_idname = "sn.add_enum_item"
    bl_label = "Add Enum Item"
    bl_description = "Adds an enum item to this property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    item_data_path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        items = eval(self.item_data_path)
        item = items.add()
        item.update(context)
        return {"FINISHED"}



class SN_OT_RemoveEnumItem(bpy.types.Operator):
    bl_idname = "sn.remove_enum_item"
    bl_label = "Remove Enum Item"
    bl_description = "Removes an enum item from this property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    settings_data_path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    icon_index: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        settings = eval(self.settings_data_path)
        settings.items.remove(self.icon_index)
        settings.compile(context)
        return {"FINISHED"}



class SN_OT_AddPropertyItem(bpy.types.Operator):
    bl_idname = "sn.add_property_item"
    bl_label = "Add Property"
    bl_description = "Adds a property to this group"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    group_data_path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        prop = eval(self.group_data_path)
        new_prop = prop.settings.properties.add()
        new_prop.name = "New Property"
        return {"FINISHED"}



class SN_OT_AddPropertyNodePopup(bpy.types.Operator):
    bl_idname = "sn.add_property_node_popup"
    bl_label = "Add Property Node Popup"
    bl_description = "Opens a popup to let you choose a property node"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.scale_y = 1.5
        op = col.operator("sn.add_property_node", text="Property", icon="ADD")
        op.type = "SN_SerpensPropertyNode"
        op = col.operator("sn.add_property_node", text="Display Property", icon="ADD")
        op.type = "SN_DisplayPropertyNode"
        op = col.operator("sn.add_property_node", text="Set Property", icon="ADD")
        op.type = "SN_SetPropertyNode"
        op = col.operator("sn.add_property_node", text="On Property Update", icon="ADD")
        op.type = "SN_OnPropertyUpdateNode"
        
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self)
    
    

class SN_OT_AddPropertyNode(bpy.types.Operator):
    bl_idname = "sn.add_property_node"
    bl_label = "Add Property Node"
    bl_description = "Adds this node to the editor"
    bl_options = {"REGISTER", "INTERNAL"}

    type: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        bpy.ops.node.add_node("INVOKE_DEFAULT", type=self.type, use_transform=True)
        node = context.space_data.node_tree.nodes.active

        if context.scene.sn.property_index < len(context.scene.sn.properties):
            prop = context.scene.sn.properties[context.scene.sn.property_index]

            if self.type == "SN_SerpensPropertyNode":
                node.prop_name = prop.name
            elif self.type == "SN_OnPropertyUpdateNode":
                node.prop_name = prop.name
        return {"FINISHED"}
    
    
    
class SN_OT_FindProperty(bpy.types.Operator):
    bl_idname = "sn.find_property"
    bl_label = "Find Property"
    bl_description = "Finds this property in the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        
        # init property nodes
        empty_nodes = []
        property_nodes = []
        property = None
        if context.scene.sn.property_index < len(context.scene.sn.properties):
            property = context.scene.sn.properties[context.scene.sn.property_index]

        # find property nodes
        for ngroup in bpy.data.node_groups:
            if ngroup.bl_idname == "ScriptingNodesTree":
                for node in ngroup.nodes:
                    if node.bl_idname == "SN_SerpensPropertyNode":
                        prop_src = node.get_prop_source()
                        if prop_src and node.prop_name in prop_src.properties:
                            prop = prop_src.properties[node.prop_name]
                            if prop == property:
                                property_nodes.append(node)
                        elif not prop_src or not node.prop_name:
                            empty_nodes.append(node)
                        
        # draw nodes for selected property    
        if context.scene.sn.property_index < len(context.scene.sn.properties):
            col = layout.column()
            row = col.row()
            row.enabled = False
            row.label(text=f"Property: {property.name}")
            
            for node in property_nodes:
                op = col.operator("sn.find_node", text=node.name, icon="RESTRICT_SELECT_OFF")
                op.node_tree = node.node_tree.name
                op.node = node.name
            
            if not property_nodes:
                col.label(text="No nodes found for this property", icon="INFO")
        
        # draw nodes with empty property
        col = layout.column()
        row = col.row()
        row.label(text="Empty Propert Nodes")
        row.enabled = False
        
        for node in empty_nodes:
            op = col.operator("sn.find_node", text=node.name, icon="RESTRICT_SELECT_OFF")
            op.node_tree = node.node_tree.name
            op.node = node.name

        if not empty_nodes:
            col.label(text="No empty property nodes found", icon="INFO")
    
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=250)