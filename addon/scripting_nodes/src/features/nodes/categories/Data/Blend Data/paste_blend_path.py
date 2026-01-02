import bpy
import re
from typing import List, Tuple, Optional

from ......lib.utils.blend_data.path_utils import (
    parse_blend_data_path,
    infer_output_type as _infer_output_type,
)


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
        # Get clipboard content
        clipboard = context.window_manager.clipboard

        if not clipboard:
            self.report({"WARNING"}, "Clipboard is empty")
            return {"CANCELLED"}

        if not clipboard.startswith("bpy."):
            self.report({"WARNING"}, "Clipboard doesn't contain a valid bpy path")
            return {"CANCELLED"}

        # Parse the path
        segments = parse_blend_data_path(clipboard)

        if not segments:
            self.report({"WARNING"}, f"Could not parse path: {clipboard}")
            return {"CANCELLED"}

        ntree = context.space_data.node_tree

        # Get cursor location for node placement
        try:
            loc_x = context.space_data.cursor_location[0]
            loc_y = context.space_data.cursor_location[1]
        except:
            loc_x = 0
            loc_y = 0

        created_nodes = []
        node_spacing = 200

        for i, segment in enumerate(segments):
            x_offset = i * node_spacing

            # Create Blend Data node
            node = ntree.nodes.new("SNA_Node_BlendData")
            node.location = (loc_x + x_offset, loc_y)

            # Configure the node
            node.setup_from_path(
                path=segment["path"],
                is_root=segment["is_root"],
                access_mode=segment["access"],
                output_type=segment["output_type"],
                input_name=segment.get("input_name", "Data"),
            )

            # Set access value if applicable
            if segment["access"] == "INDEX" and "access_value" in segment:
                for inp in node.inputs:
                    if inp.name == "Index":
                        inp.default_value = segment["access_value"]
                        break
            elif segment["access"] == "NAME" and "access_value" in segment:
                for inp in node.inputs:
                    if inp.name == "Name":
                        inp.default_value = str(segment["access_value"])
                        break

            created_nodes.append(node)

        # Connect nodes together
        for i in range(len(created_nodes) - 1):
            from_node = created_nodes[i]
            to_node = created_nodes[i + 1]

            # Find output socket (first one)
            from_socket = from_node.outputs[0] if from_node.outputs else None

            # Find BlendData input socket
            to_socket = None
            for inp in to_node.inputs:
                if inp.bl_idname == "ScriptingBlendDataSocket":
                    to_socket = inp
                    break

            if from_socket and to_socket:
                ntree.links.new(from_socket, to_socket)

        # Select created nodes
        for node in ntree.nodes:
            node.select = node in created_nodes
        if created_nodes:
            ntree.nodes.active = created_nodes[-1]

        self.report({"INFO"}, f"Created {len(created_nodes)} node(s) from path")

        # Start moving nodes with mouse
        bpy.ops.transform.translate("INVOKE_DEFAULT")

        return {"FINISHED"}
