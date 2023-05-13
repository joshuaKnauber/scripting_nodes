import bpy


class SN_OT_AddGroupCategory(bpy.types.Operator):
    bl_idname = "sn.add_group_category"
    bl_label = "Add Category"
    bl_description = "Add a new node group category"
    bl_options = {"REGISTER", "UNDO"}

    name: bpy.props.StringProperty(
        name="Name", default="New Category", options={"SKIP_SAVE"})

    def execute(self, context):
        sn = context.scene.sn
        item = sn.groups.add()
        item.name = self.name
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class SN_OT_MoveGroupCategory(bpy.types.Operator):
    bl_idname = "sn.move_group_category"
    bl_label = "Move Group"
    bl_description = "Move a group to another category"
    bl_options = {"REGISTER", "UNDO"}

    ntree: bpy.props.StringProperty(
        name="Name", default="", options={"SKIP_SAVE"})

    def category_items(self, context):
        items = [("Other", "Other", "")]
        for group in context.scene.sn.groups:
            items.append((group.name, group.name, ""))
        return items

    category: bpy.props.EnumProperty(
        name="Category", items=category_items, description="Category to move to"
    )

    def execute(self, context):
        ntree = bpy.data.node_groups[self.ntree]
        ntree.category = self.category
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, "category", expand=True)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class SN_OT_AddGroupNode(bpy.types.Operator):
    bl_idname = "sn.add_group_node"
    bl_label = "Add Group"
    bl_description = "Add this node group"
    bl_options = {"REGISTER", "UNDO"}

    ntree: bpy.props.StringProperty(name="Node Tree", default="")

    def execute(self, context):
        bpy.ops.node.add_node(
            "INVOKE_DEFAULT", type="SN_NodeGroupNode", use_transform=True)
        node = context.active_node
        node.group_tree = bpy.data.node_groups[self.ntree]
        return {"FINISHED"}
