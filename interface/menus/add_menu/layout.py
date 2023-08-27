import bpy


class SN_MT_LayoutMenu(bpy.types.Menu):
    bl_idname = "SN_MT_LayoutMenu"
    bl_label = "Layout"

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        op = layout.operator("node.add_node", text="Frame")
        op.type = "NodeFrame"
        op.use_transform = True

        op = layout.operator("node.add_node", text="Portal")
        # op.type = SN_PortalNode.bl_idname
        op.use_transform = True

        op = layout.operator("node.add_node", text="Reroute")
        op.type = "NodeReroute"
        op.use_transform = True
