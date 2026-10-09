"""Event nodes: run their flow from a Blender app handler (bpy.app.handlers)."""

import bpy

from ....core import naming
from ...base_node import ScriptingBaseNode
from ....sockets.spec import Logic


class EventNode(ScriptingBaseNode):
    """Base of the handler-based events. Subclasses list their handlers as
    {label: handler name}; with more than one, the node gets a switch."""

    sn_root = True
    sn_outputs = [Logic()]
    handlers: dict = {}

    def emit(self, ctx):
        handler = self.handler
        name = ctx.name("function")
        ctx.imports("from bpy.app.handlers import persistent")
        ctx.module(f"""
            @persistent
            def {name}(*args):
                {ctx.flow("flow")}
        """)
        ctx.on_register(f"bpy.app.handlers.{handler}.append({name})")
        ctx.on_unregister(f"bpy.app.handlers.{handler}.remove({name})")

    def sn_names(self):
        return [naming.Symbol("function", f"on_{self.handler}")]

    @property
    def handler(self):
        return getattr(self, "when", None) or next(iter(self.handlers.values()))

    def draw(self, context, layout):
        if len(self.handlers) > 1:
            layout.prop(self, "when", expand=True)


def event_node(idname, label, handlers, description=""):
    """Create an event node class for the given {label: handler} choices."""
    annotations = {}
    if len(handlers) > 1:
        annotations["when"] = bpy.props.EnumProperty(
            name="When", items=[(h, text, "") for text, h in handlers.items()]
        )
    return type(
        idname,
        (EventNode, bpy.types.Node),
        {
            "bl_idname": idname,
            "bl_label": label,
            "bl_description": description,
            "handlers": handlers,
            "__annotations__": annotations,
            "__module__": __name__,
        },
    )


BEFORE_AFTER = ("Before", "After")


def _pair(name):
    return dict(zip(BEFORE_AFTER, (f"{name}_pre", f"{name}_post")))


SNA_Node_OnLoad = event_node("SNA_Node_OnLoad", "On Load", _pair("load"))
SNA_Node_OnSave = event_node("SNA_Node_OnSave", "On Save", _pair("save"))
SNA_Node_OnUndo = event_node("SNA_Node_OnUndo", "On Undo", _pair("undo"))
SNA_Node_OnRedo = event_node("SNA_Node_OnRedo", "On Redo", _pair("redo"))
SNA_Node_OnFrameChange = event_node(
    "SNA_Node_OnFrameChange", "On Frame Change", _pair("frame_change")
)
SNA_Node_OnDepsgraphUpdate = event_node(
    "SNA_Node_OnDepsgraphUpdate", "On Depsgraph Update", _pair("depsgraph_update")
)
SNA_Node_OnRenderStart = event_node(
    "SNA_Node_OnRenderStart", "On Render Start", {"Before": "render_pre"}
)
SNA_Node_OnRenderFinish = event_node(
    "SNA_Node_OnRenderFinish", "On Render Finish", {"After": "render_post", "Complete": "render_complete"}
)  # fmt: skip


class SNA_Node_OnBlenderClose(ScriptingBaseNode, bpy.types.Node):
    """Runs when Blender quits."""

    bl_idname = "SNA_Node_OnBlenderClose"
    bl_label = "On Blender Close"
    sn_root = True
    sn_outputs = [Logic()]

    def sn_names(self):
        return [naming.Symbol("function", "on_blender_close")]

    def emit(self, ctx):
        name = ctx.name("function")
        ctx.imports("import atexit")
        ctx.module(f"""
            def {name}():
                {ctx.flow("flow")}
        """)
        ctx.on_register(f"atexit.register({name})")
        ctx.on_unregister(f"atexit.unregister({name})")
