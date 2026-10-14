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
            layout.prop(self, "when", expand=len(self.handlers) <= 3)


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


# new choices go at the end: saved nodes store the choice's position
SNA_Node_OnLoad = event_node(
    "SNA_Node_OnLoad", "On Load", {**_pair("load"), "Failed": "load_post_fail"}
)
SNA_Node_OnSave = event_node(
    "SNA_Node_OnSave", "On Save", {**_pair("save"), "Failed": "save_post_fail"}
)
SNA_Node_OnUndo = event_node("SNA_Node_OnUndo", "On Undo", _pair("undo"))
SNA_Node_OnRedo = event_node("SNA_Node_OnRedo", "On Redo", _pair("redo"))
SNA_Node_OnFrameChange = event_node(
    "SNA_Node_OnFrameChange", "On Frame Change", _pair("frame_change")
)
SNA_Node_OnDepsgraphUpdate = event_node(
    "SNA_Node_OnDepsgraphUpdate", "On Depsgraph Update", _pair("depsgraph_update")
)
SNA_Node_OnRenderStart = event_node(
    "SNA_Node_OnRenderStart",
    "On Render Start",
    {"Each Frame": "render_pre", "Once": "render_init"},
    "Before a frame renders, or once when a render (or animation) starts",
)
SNA_Node_OnRenderFinish = event_node(
    "SNA_Node_OnRenderFinish",
    "On Render Finish",
    {
        "Each Frame": "render_post",
        "Complete": "render_complete",
        "Cancel": "render_cancel",
        "Frame Saved": "render_write",
    },
    "After a frame rendered, when the render is done or cancelled, or after "
    "an animation frame was saved",
)
SNA_Node_OnPlayback = event_node(
    "SNA_Node_OnPlayback",
    "On Playback",
    {"Start": "animation_playback_pre", "Stop": "animation_playback_post"},
    "When animation playback starts or stops",
)
SNA_Node_OnBake = event_node(
    "SNA_Node_OnBake",
    "On Bake",
    {
        "Start": "object_bake_pre",
        "Complete": "object_bake_complete",
        "Cancel": "object_bake_cancel",
    },
    "When baking (Cycles' Bake button) starts, finishes or is cancelled",
)
SNA_Node_OnComposite = event_node(
    "SNA_Node_OnComposite",
    "On Composite",
    {**_pair("composite"), "Cancel": "composite_cancel"},
    "Around the compositor running",
)
SNA_Node_OnImport = event_node(
    "SNA_Node_OnImport",
    "On Append or Link",
    _pair("blend_import"),
    "Before or after data is appended or linked from another .blend file",
)


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
