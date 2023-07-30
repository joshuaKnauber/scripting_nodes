import bpy
from .... import auto_load


class SN_OT_SearchNodes(bpy.types.Operator):
    bl_idname = "sn.search_nodes"
    bl_label = "Search"
    bl_description = "Search for Serpens nodes"
    bl_options = {"REGISTER", "UNDO"}
    bl_property = "node"

    def node_items(self, context: bpy.types.Context):
        items = []
        for cls in auto_load.ordered_classes:
            if cls.bl_rna.base and cls.bl_rna.base.identifier == "Node":
                items.append((cls.bl_idname, cls.bl_label, cls.bl_label))
        items.append(("NodeFrame", "Frame", "Frame"))
        items.append(("NodeReroute", "Reroute", "Reroute"))
        items = sorted(items, key=lambda x: x[1])
        return items

    node: bpy.props.EnumProperty(
        name="Node", items=node_items, description="Node to add", options={"SKIP_SAVE"}
    )

    def execute(self, context: bpy.types.Context):
        node = self.node
        bpy.ops.node.add_node("INVOKE_DEFAULT", type=node, use_transform=True)
        return {"FINISHED"}

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {"FINISHED"}
