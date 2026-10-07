"""Blend Data node - one segment of a pasted Blender data path.

A path like `bpy.data.objects["Cube"].data.name` is split at its subscripts
into a chain of nodes (see blend_data/path_utils.parse_blend_data_path):

    [bpy.data.objects, by name "Cube"] -> [data.name]
"""

import bpy

from .....blend_data.path_utils import (
    get_label_from_path,
    get_socket_name_from_path,
    is_data_path,
    parse_blend_data_path,
)
from .....core.context import NodeError
from .....sockets.spec import BlendData, Integer, Socket, String
from ....base_node import ScriptingBaseNode

OUTPUT_TYPES = [
    ("ScriptingBlendDataSocket", "Blend Data", "Blend Data reference"),
    ("ScriptingStringSocket", "String", "String value"),
    ("ScriptingIntegerSocket", "Integer", "Integer value"),
    ("ScriptingFloatSocket", "Float", "Float value"),
    ("ScriptingBooleanSocket", "Boolean", "Boolean value"),
]


class SNA_Node_BlendData(ScriptingBaseNode, bpy.types.Node):
    """Access Blend Data by path"""

    bl_idname = "SNA_Node_BlendData"
    bl_label = "Blend Data"

    data_path: bpy.props.StringProperty(
        name="Path", description="The blend data path this node accesses"
    )
    is_root: bpy.props.BoolProperty(
        name="Is Root",
        description="The path starts at bpy (no input needed)",
        default=True,
    )
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
    output_type: bpy.props.EnumProperty(
        name="Output Type", description="Type of the output", items=OUTPUT_TYPES
    )
    input_name: bpy.props.StringProperty(name="Input Name", default="Data")

    def socket_specs(self):
        if not self.data_path:
            return [], []  # configured from the clipboard first
        inputs = []
        if not self.is_root:
            inputs.append(BlendData("data", self.input_name or "Data"))
        if self.access_mode == "INDEX":
            inputs.append(Integer("index", "Index"))
        elif self.access_mode == "NAME":
            inputs.append(String("name", "Name"))
        name = get_socket_name_from_path(self.data_path, self.access_mode)
        return inputs, [Socket(self.output_type, "value", name)]

    def setup_from_path(
        self,
        path: str,
        is_root: bool = True,
        access_mode: str = "NONE",
        output_type: str = "ScriptingBlendDataSocket",
        input_name: str = "Data",
        access_value=None,
    ):
        """Configure the node from a parsed path segment."""
        self.data_path = path
        self.is_root = is_root
        self.access_mode = access_mode
        self.output_type = output_type
        self.input_name = input_name
        self.label = get_label_from_path(path, access_mode)
        self.sync_sockets()
        if access_value is not None:
            if access_mode == "INDEX":
                self.socket("index").value = int(access_value)
            elif access_mode == "NAME":
                self.socket("name").value = str(access_value)

    def draw(self, context, layout):
        if not self.data_path:
            op = layout.operator(
                "sna.setup_blend_data_node",
                text="Setup from Clipboard",
                icon="PASTEDOWN",
            )
            op.node_name = self.name
        elif self.access_mode != "NONE":
            layout.prop(self, "access_mode", text="")

    def emit(self, ctx):
        if not self.data_path:
            raise NodeError("Paste a data path")
        # the path comes from the clipboard and ends up in the code
        if not is_data_path(self.data_path):
            raise NodeError(f"Invalid data path: {self.data_path}")
        if self.is_root:
            path = self.data_path
        else:
            if not ctx.is_linked("data"):
                raise NodeError(f"Connect the {self.input_name or 'Data'} input")
            path = f"{ctx.input('data')}.{self.data_path}"
        if self.access_mode == "INDEX":
            path = f"{path}[{ctx.input('index')}]"
        elif self.access_mode == "NAME":
            path = f"{path}[{ctx.input('name')}]"
        ctx.output("value", path)


def create_chain(tree, segments, location, spacing=200):
    """One Blend Data node per path segment, linked left to right."""
    nodes = []
    for i, segment in enumerate(segments):
        node = tree.nodes.new(SNA_Node_BlendData.bl_idname)
        node.location = (location[0] + i * spacing, location[1])
        node.setup_from_path(
            path=segment["path"],
            is_root=segment["is_root"],
            access_mode=segment["access"],
            output_type=segment["output_type"],
            input_name=segment.get("input_name", "Data"),
            access_value=segment.get("access_value"),
        )
        if nodes:
            source, target = nodes[-1].socket("value", output=True), node.socket("data")
            if source is not None and target is not None:
                tree.links.new(source, target)
        nodes.append(node)
    return nodes


def parse_clipboard(operator, context):
    """Segments of the bpy path in the clipboard, or None (reported)."""
    clipboard = context.window_manager.clipboard.strip()
    if not clipboard:
        operator.report({"WARNING"}, "Clipboard is empty")
        return None
    if not clipboard.startswith("bpy."):
        operator.report({"WARNING"}, "Clipboard doesn't contain a valid bpy path")
        return None
    segments = parse_blend_data_path(clipboard)
    if not segments:
        operator.report({"WARNING"}, f"Could not parse path: {clipboard}")
        return None
    return segments


class SNA_OT_SetupBlendDataNode(bpy.types.Operator):
    """Set up the Blend Data node from the path in the clipboard"""

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
        tree = context.space_data.node_tree
        node = tree.nodes.get(self.node_name)
        if not node:
            self.report({"WARNING"}, "Node not found")
            return {"CANCELLED"}
        segments = parse_clipboard(self, context)
        if segments is None:
            return {"CANCELLED"}

        first = segments[0]
        node.setup_from_path(
            path=first["path"],
            is_root=first["is_root"],
            access_mode=first["access"],
            output_type=first["output_type"],
            input_name=first.get("input_name", "Data"),
            access_value=first.get("access_value"),
        )
        nodes = [node]
        if len(segments) > 1:
            x, y = node.location
            rest = create_chain(tree, segments[1:], (x + 200, y))
            tree.links.new(node.socket("value", output=True), rest[0].socket("data"))
            nodes += rest

        for other in tree.nodes:
            other.select = other in nodes
        tree.nodes.active = nodes[-1]
        self.report({"INFO"}, f"Created {len(nodes)} node(s) from path")
        return {"FINISHED"}
