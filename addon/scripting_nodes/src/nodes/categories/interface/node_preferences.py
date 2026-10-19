"""Addon Preferences: the `bpy.types.AddonPreferences` class of the generated
addon. Its properties (sidebar) are the add-on's settings, the Draw flow lays
out the preferences UI.

Only one per addon makes sense (Blender allows one preferences class per
addon); extra ones fail to register.

Blender only draws an add-on's preferences when the add-on is in its add-on
list (saved with the user's preferences); the live add-on isn't. Preview runs
the generated draw() in a popup on a stand-in: a property group with the same
properties on the window manager, so fields work but values are the preview's.
"""

import bpy

from ....core import naming, runtime
from ....sockets.spec import Interface
from ..._property_list import SELF, PropertyListMixin
from ...base_node import ScriptingBaseNode


class SNA_Node_Preferences(PropertyListMixin, ScriptingBaseNode, bpy.types.Node):
    """The preferences of the addon (shown in Preferences > Add-ons)."""

    bl_idname = "SNA_Node_Preferences"
    bl_label = "Preferences"
    sn_root = True
    sn_outputs = [Interface("draw", "Draw")]

    def sn_names(self):
        return [naming.Class("class", "AP", "preferences")]

    def draw(self, context, layout):
        self.draw_property_names(layout)
        op = layout.operator("sna.preview_preferences", icon="HIDE_OFF")
        op.node_id = self.id

    def emit(self, ctx):
        # its fields get `self` as the preferences in draw (_property_target)
        # bl_idname must be the add-on's package, the one of tree modules
        ctx.module(f"""
            class {ctx.name("class")}(bpy.types.AddonPreferences):
                bl_idname = __package__
                {ctx.join(self.annotations(ctx))}

                def draw(self, context):
                    {ctx.flow("draw", layout="self.layout", outputs={SELF: "self"})}
        """)


# -- preview -----------------------------------------------------------------

_stand_in = {"for": None, "class": None}
PREVIEW_ATTR = "sna_preferences_preview"
_LEFT_OUT = {"update", "get", "set", "get_transform", "set_transform"}


def live_preferences_class():
    """The generated add-on's AddonPreferences class, None if it has none."""
    module = runtime.loaded_module()
    if not module:
        return None
    for cls in bpy.types.AddonPreferences.__subclasses__():
        if cls.__module__.split(".")[0] == module and getattr(
            cls, "is_registered", False
        ):
            return cls
    return None


def _remove_stand_in():
    cls = _stand_in["class"]
    if cls is not None:
        if hasattr(bpy.types.WindowManager, PREVIEW_ATTR):
            delattr(bpy.types.WindowManager, PREVIEW_ATTR)
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
    _stand_in.update({"for": None, "class": None})


def stand_in(prefs_cls):
    """The window manager's stand-in for `prefs_cls` (made again when the
    add-on was rebuilt): the same properties, without callbacks into the
    add-on's code."""
    if _stand_in["for"] is not prefs_cls:
        _remove_stand_in()
        annotations = {}
        for name, prop in getattr(prefs_cls, "__annotations__", {}).items():
            keywords = {k: v for k, v in prop.keywords.items() if k not in _LEFT_OUT}
            annotations[name] = prop.function(**keywords)
        cls = type(
            "SNA_PG_PreferencesPreview",
            (bpy.types.PropertyGroup,),
            {"__annotations__": annotations, "layout": None},
        )
        bpy.utils.register_class(cls)
        setattr(
            bpy.types.WindowManager, PREVIEW_ATTR, bpy.props.PointerProperty(type=cls)
        )
        _stand_in.update({"for": prefs_cls, "class": cls})
    return getattr(bpy.context.window_manager, PREVIEW_ATTR)


class SNA_OT_PreviewPreferences(bpy.types.Operator):
    """Show the preferences as they will look in Preferences > Add-ons
    (values changed here are only the preview's)"""

    bl_idname = "sna.preview_preferences"
    bl_label = "Preview"
    bl_options = {"INTERNAL"}

    node_id: bpy.props.StringProperty(options={"HIDDEN"})

    def invoke(self, context, event):
        prefs_cls = live_preferences_class()
        if prefs_cls is None:
            self.report({"WARNING"}, "The add-on isn't running (see the node's error)")
            return {"CANCELLED"}
        stand_in(prefs_cls)  # not while drawing: registers a class
        return context.window_manager.invoke_popup(self, width=500)

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Preferences Preview", icon="PREFERENCES")
        prefs_cls = live_preferences_class()
        if prefs_cls is None or _stand_in["for"] is not prefs_cls:
            layout.label(text="The add-on changed, open the preview again")
            return
        preview = getattr(context.window_manager, PREVIEW_ATTR)
        box = layout.box()
        type(preview).layout = box
        try:
            prefs_cls.draw(preview, context)
        except Exception as exc:  # noqa: BLE001 - shown on the node too
            box.label(text=f"{type(exc).__name__}: {exc}", icon="ERROR")
        finally:
            type(preview).layout = None


def unregister():
    _remove_stand_in()
