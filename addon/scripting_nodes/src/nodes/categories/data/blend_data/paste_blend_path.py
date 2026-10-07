import bpy

from .node_blend_data import create_chain, parse_clipboard


class SNA_OT_PasteBlendDataPath(bpy.types.Operator):
    """Paste a blend data path and create nodes to represent it"""

    bl_idname = "sna.paste_blend_data_path"
    bl_label = "Paste Blend Data Path"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (
            context.space_data
            and context.space_data.type == "NODE_EDITOR"
            and context.space_data.node_tree
            and context.space_data.node_tree.bl_idname == "ScriptingNodeTree"
        )

    def execute(self, context):
        segments = parse_clipboard(self, context)
        if segments is None:
            return {"CANCELLED"}
        tree = context.space_data.node_tree
        location = getattr(context.space_data, "cursor_location", (0, 0))
        nodes = create_chain(tree, segments, location)

        for node in tree.nodes:
            node.select = node in nodes
        tree.nodes.active = nodes[-1]
        self.report({"INFO"}, f"Created {len(nodes)} node(s) from path")
        # move the new nodes with the mouse
        bpy.ops.transform.translate("INVOKE_DEFAULT")
        return {"FINISHED"}
