from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.lib.utils.blend_data.path_utils import (
    format_name,
    get_label_from_path,
    get_socket_name_from_path,
)
import bpy


class SNA_Node_BlendData(ScriptingBaseNode, bpy.types.Node):
    """Access Blend Data by path"""

    bl_idname = "SNA_Node_BlendData"
    bl_label = "Blend Data"

    # The internal path this node represents (not user-editable)
    data_path: bpy.props.StringProperty(
        name="Path",
        description="The blend data path this node accesses",
        default="",
    )

    # Whether this node needs an input or is a root accessor
    is_root: bpy.props.BoolProperty(
        name="Is Root",
        description="Whether this is a root data accessor (no input needed)",
        default=True,
    )

    # Access mode for collections
    access_mode: bpy.props.EnumProperty(
        name="Access Mode",
        description="How to access items in collections",
        items=[
            ("NONE", "None", "No collection access"),
            ("INDEX", "By Index", "Access by numeric index"),
            ("NAME", "By Name", "Access by name string"),
        ],
        default="NONE",
    )

    # Store the output type as string for recreating socket
    output_type: bpy.props.EnumProperty(
        name="Output Type",
        description="Type of the output socket",
        items=[
            ("ScriptingBlendDataSocket", "Blend Data", "Blend Data reference"),
            ("ScriptingStringSocket", "String", "String value"),
            ("ScriptingIntegerSocket", "Integer", "Integer value"),
            ("ScriptingFloatSocket", "Float", "Float value"),
            ("ScriptingBooleanSocket", "Boolean", "Boolean value"),
        ],
        default="ScriptingBlendDataSocket",
    )

    # Store input name for recreation
    input_name: bpy.props.StringProperty(
        name="Input Name",
        default="Data",
    )

    def on_create(self):
        # Start with no sockets - user configures via setup
        pass

    def draw(self, context, layout):
        # If not configured, show setup button
        if not self.data_path:
            layout.operator(
                "sna.setup_blend_data_node",
                text="Setup from Clipboard",
                icon="PASTEDOWN",
            ).node_name = self.name
        else:
            # Show access mode controls if this is a collection accessor
            if self.access_mode != "NONE":
                layout.prop(self, "access_mode", text="")

    def setup_from_path(
        self,
        path: str,
        is_root: bool = True,
        access_mode: str = "NONE",
        output_type: str = "ScriptingBlendDataSocket",
        input_name: str = "Data",
    ):
        """Configure the node from a parsed path segment."""
        self.data_path = path
        self.is_root = is_root
        self.access_mode = access_mode
        self.output_type = output_type
        self.input_name = input_name

        # Update node label with readable name
        self.label = get_label_from_path(path, access_mode)

        # Clear existing sockets and recreate
        self.inputs.clear()
        self.outputs.clear()

        # Get socket name from path
        output_name = get_socket_name_from_path(path, access_mode)

        # Add input socket if not root
        if not is_root:
            self.add_input("ScriptingBlendDataSocket", input_name)

        # Add access sockets based on mode
        if access_mode == "INDEX":
            self.add_input("ScriptingIntegerSocket", "Index")
        elif access_mode == "NAME":
            self.add_input("ScriptingStringSocket", "Name")

        # Add output socket with correct type and name
        self.add_output(output_type, output_name)

        self._generate()

    def generate(self):
        if len(self.outputs) == 0:
            return

        out_socket = self.outputs[0]

        # Build the code path
        if self.is_root:
            # Root node - use path directly
            base_path = self.data_path
        else:
            # Non-root - needs input (first BlendData socket)
            data_input = None
            for inp in self.inputs:
                if inp.bl_idname == "ScriptingBlendDataSocket":
                    data_input = inp
                    break

            if data_input and data_input.is_linked:
                input_code = data_input.eval()
                if self.data_path:
                    base_path = f"{input_code}.{self.data_path}"
                else:
                    base_path = input_code
            else:
                out_socket.code = "None"
                return

        # Apply collection access if needed
        if self.access_mode == "INDEX":
            index_input = None
            for inp in self.inputs:
                if inp.name == "Index":
                    index_input = inp
                    break
            if index_input:
                index_code = index_input.eval()
                out_socket.code = f"{base_path}[{index_code}]"
            else:
                out_socket.code = f"{base_path}[0]"
        elif self.access_mode == "NAME":
            name_input = None
            for inp in self.inputs:
                if inp.name == "Name":
                    name_input = inp
                    break
            if name_input:
                name_code = name_input.eval()
                out_socket.code = f"{base_path}[{name_code}]"
            else:
                out_socket.code = f'{base_path}[""]'
        else:
            out_socket.code = base_path


class SNA_OT_SetupBlendDataNode(bpy.types.Operator):
    """Setup the Blend Data node from clipboard path"""

    bl_idname = "sna.setup_blend_data_node"
    bl_label = "Setup Blend Data Node"
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

        # Import the parser
        from .paste_blend_path import parse_blend_data_path, _infer_output_type

        segments = parse_blend_data_path(clipboard)

        if not segments:
            self.report({"WARNING"}, f"Could not parse path: {clipboard}")
            return {"CANCELLED"}

        # Setup the first node (the one with the button)
        first_segment = segments[0]

        node.setup_from_path(
            path=first_segment["path"],
            is_root=first_segment["is_root"],
            access_mode=first_segment["access"],
            output_type=first_segment["output_type"],
            input_name=first_segment.get("input_name", "Data"),
        )

        # Set access value if applicable
        if first_segment["access"] == "INDEX" and "access_value" in first_segment:
            for inp in node.inputs:
                if inp.name == "Index":
                    inp.default_value = first_segment["access_value"]
                    break
        elif first_segment["access"] == "NAME" and "access_value" in first_segment:
            for inp in node.inputs:
                if inp.name == "Name":
                    inp.default_value = str(first_segment["access_value"])
                    break

        created_nodes = [node]
        node_spacing = 200

        # Create additional nodes for remaining segments
        for i, segment in enumerate(segments[1:], start=1):
            x_offset = i * node_spacing

            new_node = ntree.nodes.new("SNA_Node_BlendData")
            new_node.location = (node.location[0] + x_offset, node.location[1])

            new_node.setup_from_path(
                path=segment["path"],
                is_root=segment["is_root"],
                access_mode=segment["access"],
                output_type=segment["output_type"],
                input_name=segment.get("input_name", "Data"),
            )

            # Set access value if applicable
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

        # Connect nodes together
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

        # Select created nodes
        for n in ntree.nodes:
            n.select = n in created_nodes
        if created_nodes:
            ntree.nodes.active = created_nodes[-1]

        self.report({"INFO"}, f"Created {len(created_nodes)} node(s) from path")
        return {"FINISHED"}
