"""
Operators for pasting and clearing blend data paths on interface nodes.
"""

import bpy


class SNA_OT_BlendDataPastePath(bpy.types.Operator):
    """Paste a blend data path and configure the node"""

    bl_idname = "sna.blend_data_paste_path"
    bl_label = "Paste Blend Data Path"
    bl_description = "Paste a blend data path and configure the node"
    bl_options = {"REGISTER", "UNDO"}

    node_name: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return (
            context.space_data
            and context.space_data.type == "NODE_EDITOR"
            and context.space_data.node_tree
        )

    def execute(self, context):
        ntree = context.space_data.node_tree
        node = ntree.nodes.get(self.node_name)

        if not node:
            self.report({"WARNING"}, "Node not found")
            return {"CANCELLED"}

        clipboard = context.window_manager.clipboard

        if not clipboard:
            self.report({"WARNING"}, "Clipboard is empty")
            return {"CANCELLED"}

        if not clipboard.startswith("bpy."):
            self.report({"WARNING"}, "Clipboard doesn't contain a valid bpy path")
            return {"CANCELLED"}

        from scripting_nodes.src.lib.utils.blend_data.path_utils import (
            parse_blend_data_path,
        )

        segments = parse_blend_data_path(clipboard)

        if not segments:
            self.report({"WARNING"}, f"Could not parse path: {clipboard}")
            return {"CANCELLED"}

        # The last segment contains the property we want to display
        last_segment = segments[-1]
        last_path = last_segment["path"]

        # Get the property name (last part of the path)
        path_parts = last_path.split(".")
        prop_name = path_parts[-1]

        # Determine if we need preceding segments (blend data nodes)
        if len(segments) == 1:
            # Only one segment - check if it needs splitting
            if len(path_parts) > 1:
                # Path like "bpy.context.scene.name" - data is everything except last part
                data_path = ".".join(last_path.split(".")[:-1])
                needs_input = False
                node.setup_from_path(data_path, prop_name, needs_input)
            else:
                node.setup_from_path("", prop_name, False)
        else:
            # Multiple segments - create blend data nodes for all but the last
            if len(path_parts) > 1:
                remaining_path = ".".join(path_parts[:-1])
                segments[-1] = {
                    "path": remaining_path,
                    "is_root": False,
                    "access": "NONE",
                    "output_type": "ScriptingBlendDataSocket",
                    "input_name": segments[-1].get("input_name", "Data"),
                }
            else:
                segments = segments[:-1]

            # Create blend data nodes for the segments
            created_nodes = []
            node_spacing = 200

            for i, segment in enumerate(segments):
                x_offset = -(len(segments) - i) * node_spacing

                new_node = ntree.nodes.new("SNA_Node_BlendData")
                new_node.location = (node.location[0] + x_offset, node.location[1])

                new_node.setup_from_path(
                    path=segment["path"],
                    is_root=segment["is_root"],
                    access_mode=segment["access"],
                    output_type=segment["output_type"],
                    input_name=segment.get("input_name", "Data"),
                )

                if segment["access"] == "INDEX" and "access_value" in segment:
                    for inp in new_node.inputs:
                        if inp.name == "Index":
                            inp.default_value = segment["access_value"]
                            break
                elif segment["access"] == "NAME" and "access_value" in segment:
                    for inp in new_node.inputs:
                        if inp.name == "Name":
                            inp.default_value = str(segment["access_value"])
                            break

                created_nodes.append(new_node)

            # Connect blend data nodes together
            for i in range(len(created_nodes) - 1):
                from_node = created_nodes[i]
                to_node = created_nodes[i + 1]

                from_socket = from_node.outputs[0] if from_node.outputs else None

                to_socket = None
                for inp in to_node.inputs:
                    if inp.bl_idname == "ScriptingBlendDataSocket":
                        to_socket = inp
                        break

                if from_socket and to_socket:
                    ntree.links.new(from_socket, to_socket)

            # Connect last blend data node to this node's Data input
            if created_nodes:
                last_blend_node = created_nodes[-1]
                from_socket = (
                    last_blend_node.outputs[0] if last_blend_node.outputs else None
                )
                to_socket = node.inputs.get("Data")

                if from_socket and to_socket:
                    ntree.links.new(from_socket, to_socket)

            # Setup the node
            node.setup_from_path("", prop_name, True)

        node_label = node.bl_label.lower()
        self.report({"INFO"}, f"Configured {node_label} for property: {prop_name}")
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
        return (
            context.space_data
            and context.space_data.type == "NODE_EDITOR"
            and context.space_data.node_tree
        )

    def execute(self, context):
        ntree = context.space_data.node_tree
        node = ntree.nodes.get(self.node_name)

        if not node:
            self.report({"WARNING"}, "Node not found")
            return {"CANCELLED"}

        node.clear_blend_data_path()
        return {"FINISHED"}
