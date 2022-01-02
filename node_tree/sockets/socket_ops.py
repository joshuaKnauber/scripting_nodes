import bpy



class SN_OT_AddDynamic(bpy.types.Operator):
    bl_idname = "sn.add_dynamic"
    bl_label = "Add Dynamic Socket"
    bl_description = "Add another socket like this one"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})
    is_output: bpy.props.BoolProperty(options={"HIDDEN", "SKIP_SAVE"})
    index: bpy.props.IntProperty(options={"HIDDEN", "SKIP_SAVE"})
    insert_above: bpy.props.BoolProperty(default=False, options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return hasattr(context.space_data, "node_tree") and context.space_data.node_tree

    def execute(self, context):
        # find node in node tree
        ntree = context.space_data.node_tree
        if self.node in ntree.nodes:
            node = ntree.nodes[self.node]

            # find socket
            if self.is_output:
                socket = node.outputs[self.index]
            else:
                socket = node.inputs[self.index]
                
            # trigger adding dynamic socket
            socket.trigger_dynamic(self.insert_above)

            # trigger reevaluation
            node._evaluate(context)
        return {"FINISHED"}



class SN_OT_RemoveSocket(bpy.types.Operator):
    bl_idname = "sn.remove_socket"
    bl_label = "Remove Socket"
    bl_description = "Removes this socket"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})
    is_output: bpy.props.BoolProperty(options={"HIDDEN", "SKIP_SAVE"})
    index: bpy.props.IntProperty(options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return hasattr(context.space_data, "node_tree") and context.space_data.node_tree

    def execute(self, context):
        # find node in node tree
        ntree = context.space_data.node_tree
        if self.node in ntree.nodes:
            node = ntree.nodes[self.node]

            # find socket
            if self.is_output:
                node.outputs.remove(node.outputs[self.index])
            else:
                node.inputs.remove(node.inputs[self.index])

            # trigger reevaluation
            node._evaluate(context)
        return {"FINISHED"}



class SN_OT_SetIcon(bpy.types.Operator):
    bl_idname = "sn.set_icon"
    bl_label = "Set Icon"
    bl_description = "Sets this icon"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    icon_data_path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    prop_name: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"}, default="icon")
    icon: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        data = eval(self.icon_data_path)
        setattr(data, self.prop_name, self.icon)
        context.area.tag_redraw()
        return {"FINISHED"}



class SN_OT_SelectIcon(bpy.types.Operator):
    bl_idname = "sn.select_icon"
    bl_label = "Select Icon"
    bl_description = "Shows you a selection of all blender icons"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    bl_property = "icon_search"
    
    icon_data_path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    prop_name: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"}, default="icon")
    
    icon_search: bpy.props.StringProperty(name="Search", options={"SKIP_SAVE"})

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self,context,event):
        return context.window_manager.invoke_popup(self, width=800)

    def draw(self,context):
        layout = self.layout
        icons = bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items
        
        data = eval(self.icon_data_path)
        prop = getattr(data, self.prop_name)

        row = layout.row()
        row.prop(self,"icon_search",text="",icon="VIEWZOOM")

        grid = layout.grid_flow(align=True,even_columns=True, even_rows=True)
        for icon in icons:
            if self.icon_search.lower() in icon.name.lower() or not self.icon_search:
                op = grid.operator("sn.set_icon",text="", icon_value=icon.value, emboss=prop==icon.value)
                op.icon_data_path = self.icon_data_path
                op.prop_name = self.prop_name
                op.icon = icon.value