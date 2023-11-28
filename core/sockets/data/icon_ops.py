import bpy

from ...utils.nodes import get_node_by_id


class SNA_OT_SelectIcon(bpy.types.Operator):
    bl_idname = "sna.select_icon"
    bl_label = "Select Icon"
    bl_description = "Shows you a selection of all blender icons"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    bl_property = "icon_search"

    node: bpy.props.StringProperty()
    socket: bpy.props.IntProperty()

    icon_search: bpy.props.StringProperty(
        name="Search", options={"SKIP_SAVE", "TEXTEDIT_UPDATE"}
    )

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        icons = (
            bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items
        )

        node = get_node_by_id(self.node)
        if not node:
            return
        socket = node.inputs[self.socket]

        row = layout.row()
        row.prop(self, "icon_search", text="", icon="VIEWZOOM")

        grid = layout.grid_flow(align=True, even_columns=True, even_rows=True)
        for icon in icons:
            if self.icon_search.lower() in icon.name.lower() or not self.icon_search:
                op = grid.operator(
                    "sna.set_icon",
                    text="",
                    icon=icon.name,
                    emboss=socket.value_named == icon.name,
                )
                op.node = self.node
                op.socket = self.socket
                op.icon = icon.name

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=800)


class SNA_OT_SetIcon(bpy.types.Operator):
    bl_idname = "sna.set_icon"
    bl_label = "Set Icon"
    bl_description = "Sets the selected icon to this socket"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node: bpy.props.StringProperty()
    socket: bpy.props.IntProperty()
    icon: bpy.props.StringProperty()

    def execute(self, context):
        node = get_node_by_id(self.node)
        if node:
            socket = node.inputs[self.socket]
            socket.value_named = self.icon
        return {"FINISHED"}
