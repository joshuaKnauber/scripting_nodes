import bpy



class SN_OT_EditEnumItems(bpy.types.Operator):
    bl_idname = "sn.edit_enum_items"
    bl_label = "Edit Enum Items"
    bl_description = "Edit the enum items of this socket"
    bl_options = {"REGISTER", "INTERNAL"}

    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    is_output: bpy.props.BoolProperty(options={"SKIP_SAVE", "HIDDEN"})
    index: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        node = context.space_data.node_tree.nodes[self.node]
        socket = node.outputs[self.index] if self.is_output else node.inputs[self.index]
        
        for i, item in enumerate(socket.custom_items):
            row = layout.row(align=True)
            row.prop(item, "name", text="")
            subcol = row.column(align=True)
            subcol.enabled = i > 0
            op = subcol.operator("sn.move_enum_item_socket", text="", icon="TRIA_UP")
            op.node = self.node
            op.is_output = self.is_output
            op.index = self.index
            op.item_index = i
            op.move_up = True
            subcol = row.column(align=True)
            subcol.enabled = i < len(socket.custom_items)-1
            op = subcol.operator("sn.move_enum_item_socket", text="", icon="TRIA_DOWN")
            op.node = self.node
            op.is_output = self.is_output
            op.index = self.index
            op.item_index = i
            op.move_up = False
            row.separator()
            op = row.operator("sn.remove_enum_item_socket", text="", icon="PANEL_CLOSE", emboss=False)
            op.node = self.node
            op.is_output = self.is_output
            op.index = self.index
            op.item_index = i
        
        op = layout.operator("sn.add_enum_item_socket")
        op.node = self.node
        op.is_output = self.is_output
        op.index = self.index

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=250)



class SN_OT_AddEnumItemSocket(bpy.types.Operator):
    bl_idname = "sn.add_enum_item_socket"
    bl_label = "Add Item"
    bl_description = "Adds an enum item to this socket"
    bl_options = {"REGISTER", "INTERNAL"}

    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    is_output: bpy.props.BoolProperty(options={"SKIP_SAVE", "HIDDEN"})
    index: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        node = context.space_data.node_tree.nodes[self.node]
        socket = node.outputs[self.index] if self.is_output else node.inputs[self.index]
        socket.custom_items.add()
        return {"FINISHED"}



class SN_OT_RemoveEnumItemSocket(bpy.types.Operator):
    bl_idname = "sn.remove_enum_item_socket"
    bl_label = "Remove Item"
    bl_description = "Removes this enum item from this socket"
    bl_options = {"REGISTER", "INTERNAL"}

    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    is_output: bpy.props.BoolProperty(options={"SKIP_SAVE", "HIDDEN"})
    index: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})
    item_index: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        node = context.space_data.node_tree.nodes[self.node]
        socket = node.outputs[self.index] if self.is_output else node.inputs[self.index]
        socket.custom_items.remove(self.item_index)
        return {"FINISHED"}



class SN_OT_MoveEnumItemSocket(bpy.types.Operator):
    bl_idname = "sn.move_enum_item_socket"
    bl_label = "Move Item"
    bl_description = "Moves this enum item in this socket"
    bl_options = {"REGISTER", "INTERNAL"}

    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    is_output: bpy.props.BoolProperty(options={"SKIP_SAVE", "HIDDEN"})
    index: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})
    item_index: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})
    move_up: bpy.props.BoolProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        node = context.space_data.node_tree.nodes[self.node]
        socket = node.outputs[self.index] if self.is_output else node.inputs[self.index]
        if self.move_up:
            socket.custom_items.move(self.item_index, self.item_index-1)
        else:
            socket.custom_items.move(self.item_index, self.item_index+1)
        return {"FINISHED"}