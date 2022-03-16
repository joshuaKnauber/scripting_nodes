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