"""Opening the path browser (blend_data/browser.py) from a node, and moving
it with its path's crumbs."""

import bpy

from ...lib.trees import node_by_id
from .. import browser, locations
from ..ui import browser as ui


class SNA_OT_BrowsePath(bpy.types.Operator):
    """Browse Blender's data for this node's path"""

    bl_idname = "sna.browse_path"
    bl_label = "Blender Data"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_id: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    @classmethod
    def description(cls, context, properties):
        node = node_by_id(properties.node_id)
        function = getattr(node, "function", "")
        if node is None or not (node.path or function):
            return cls.__doc__
        code = {"CONTEXT": "context", "DATA": "bpy.data"}.get(node.path_root, "data")
        code += f".{node.path}" if node.path else ""
        code += f".{function}()" if function else ""
        return f"{cls.__doc__}: {code}"

    def invoke(self, context, event):
        node = node_by_id(self.node_id)
        if node is None:
            return {"CANCELLED"}
        state = context.window_manager.sna_browser
        browser.prepare(context)
        state.node_id = self.node_id
        state.search = ""
        browser.go(context, _start(node), getattr(node, "function", ""))
        return context.window_manager.invoke_props_dialog(
            self, width=ui.WIDTH, title="Blender Data", confirm_text="Use Path"
        )

    def draw(self, context):
        ui.draw(self.layout, context)

    def execute(self, context):
        node = node_by_id(self.node_id)
        if node is None:
            return {"CANCELLED"}
        problem = browser.problem(context)
        if problem:
            self.report({"WARNING"}, problem)
            return {"CANCELLED"}
        locations.apply_to_node(node, browser.location(context))
        if getattr(node, "sn_calls_functions", False):
            node.function = context.window_manager.sna_browser.function
        return {"FINISHED"}


def _start(node):
    """Where the browser opens: at the end of the node's path (through the
    node connected to its Data input), else where its path starts."""
    if not node.path:
        if node.path_root == "INPUT":
            return locations.input_location(node)
        return locations.Location(node.path_root)
    try:
        return locations.absolute_location(node)
    except locations.Unavailable:
        pass
    here = locations.node_location(node)
    if node.path_root == "INPUT":
        here.input_type = locations.input_location(node).input_type
    # keys from links: the first item stands for them
    here.keys = [
        key if key.mode == "ACTIVE" or key.value is not None
        else locations.Key(key.mode, 0 if key.mode == "INDEX" else "")
        for key in here.keys
    ]  # fmt: skip
    return here


class SNA_OT_BrowserGo(bpy.types.Operator):
    """Go back to this step"""

    bl_idname = "sna.browser_go"
    bl_label = "Go Back"
    bl_options = {"INTERNAL"}

    count: bpy.props.IntProperty(options={"SKIP_SAVE"})  # segments to keep

    def execute(self, context):
        browser.go(context, browser.location(context).truncated(self.count))
        return {"FINISHED"}
