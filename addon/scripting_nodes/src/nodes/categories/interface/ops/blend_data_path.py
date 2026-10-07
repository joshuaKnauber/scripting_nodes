"""Operators for pasting and clearing the Blender data path of property nodes
(PropertyTargetMixin in BLENDER mode: Checkbox, Number Field, ...)."""

import bpy

from ...data.blend_data.node_blend_data import create_chain, parse_clipboard


def _node_poll(context):
    return (
        context.space_data
        and context.space_data.type == "NODE_EDITOR"
        and context.space_data.node_tree
    )


class SNA_OT_BlendDataPastePath(bpy.types.Operator):
    """Paste a blend data path and configure the node"""

    bl_idname = "sna.blend_data_paste_path"
    bl_label = "Paste Blend Data Path"
    bl_description = "Paste a blend data path and configure the node"
    bl_options = {"REGISTER", "UNDO"}

    node_name: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return _node_poll(context)

    def execute(self, context):
        tree = context.space_data.node_tree
        node = tree.nodes.get(self.node_name)
        if not node:
            self.report({"WARNING"}, "Node not found")
            return {"CANCELLED"}
        segments = parse_clipboard(self, context)
        if segments is None:
            return {"CANCELLED"}

        # the last part of the path is the property, the rest owns it
        last = segments[-1]
        parts = last["path"].split(".")
        prop_name = parts[-1]
        owner_path = ".".join(parts[:-1])

        if len(segments) == 1:
            # e.g. bpy.context.scene.frame_end: the owner is a fixed path
            node.setup_from_path(owner_path, prop_name, False)
        else:
            # e.g. bpy.data.objects["Cube"].hide_render: Blend Data nodes
            # for the owner, connected to the Data input
            if owner_path:
                segments[-1] = {
                    "path": owner_path,
                    "is_root": False,
                    "access": "NONE",
                    "output_type": "ScriptingBlendDataSocket",
                    "input_name": last.get("input_name", "Data"),
                }
            else:
                segments = segments[:-1]
            x, y = node.location
            chain = create_chain(tree, segments, (x - 200 * len(segments), y))
            node.setup_from_path("", prop_name, True)
            data = node.socket("data")
            if chain and data is not None:
                tree.links.new(chain[-1].socket("value", output=True), data)

        self.report(
            {"INFO"}, f"Configured {node.bl_label.lower()} for property: {prop_name}"
        )
        return {"FINISHED"}


class SNA_OT_BlendDataClearPath(bpy.types.Operator):
    """Clear the blend data path configuration"""

    bl_idname = "sna.blend_data_clear_path"
    bl_label = "Clear Path"
    bl_description = "Clear the blend data path configuration"
    bl_options = {"REGISTER", "UNDO"}

    node_name: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return _node_poll(context)

    def execute(self, context):
        node = context.space_data.node_tree.nodes.get(self.node_name)
        if not node:
            self.report({"WARNING"}, "Node not found")
            return {"CANCELLED"}
        node.clear_blend_data_path()
        return {"FINISHED"}
