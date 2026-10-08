"""Group interface sockets: how our socket types appear in a tree's interface
(the sidebar "Group" tab and the Group Input / Group Output nodes).

One class per socket type, generated from the socket class: the socket's
`value` becomes the item's default and its settings (vector size, alpha,
flow kind) are copied to every socket made from the item.

    tree.interface.new_socket("Count", in_out="INPUT", socket_type="ScriptingIntegerSocket")
"""

import bpy

from .data.socket_blend_data import ScriptingBlendDataSocket
from .data.socket_boolean import ScriptingBooleanSocket
from .data.socket_color import ScriptingColorSocket
from .data.socket_data import ScriptingDataSocket
from .data.socket_float import ScriptingFloatSocket
from .data.socket_integer import ScriptingIntegerSocket
from .data.socket_list import ScriptingListSocket
from .data.socket_string import ScriptingStringSocket
from .data.socket_vector import ScriptingVectorSocket
from .flow.socket_flow import ScriptingFlowSocket

SOCKET_CLASSES = (
    ScriptingFlowSocket,
    ScriptingDataSocket,
    ScriptingBlendDataSocket,
    ScriptingStringSocket,
    ScriptingBooleanSocket,
    ScriptingFloatSocket,
    ScriptingIntegerSocket,
    ScriptingVectorSocket,
    ScriptingColorSocket,
    ScriptingListSocket,
)

# socket settings an interface item carries over to its sockets
SETTINGS = ("kind", "dimension", "use_alpha")


def _changed(self, context):
    from ..core import scheduler

    scheduler.request_full()


def _item_prop(prop, **overrides):
    """A socket property as interface item property: rebuilds on change."""
    keywords = {k: v for k, v in prop.keywords.items() if k != "update"}
    return prop.function(**{**keywords, **overrides}, update=_changed)


def _copy_settings(source, target, names):
    for name in names:
        value = getattr(source, name)
        if getattr(target, name) != value:
            setattr(target, name, value)


class _InterfaceSocket:
    has_default = False
    settings = ()

    def draw(self, context, layout):
        layout.use_property_split = True
        for name in self.settings:
            layout.prop(self, name)
        if self.has_default:
            layout.prop(self, "default_value")

    def init_socket(self, node, socket, data_path):
        _copy_settings(self, socket, self.settings)
        if self.has_default:
            socket.value = self.default_value
        socket.display_shape = socket.socket_shape
        if socket.is_output and socket.socket_type != "DATA":
            socket.link_limit = 1

    def from_socket(self, node, socket):
        # Blender passes no socket when an item is made by linking to the
        # empty socket of Group Input / Output
        if socket is None:
            return
        _copy_settings(socket, self, self.settings)
        if self.has_default:
            self.default_value = socket.value


def _interface_class(socket_cls):
    hints = socket_cls.__annotations__
    annotations = {}
    settings = tuple(name for name in SETTINGS if name in hints)
    for name in settings:
        annotations[name] = _item_prop(hints[name])
    has_default = "value" in hints
    if has_default:
        annotations["default_value"] = _item_prop(hints["value"], name="Default")
    return type(
        socket_cls.bl_idname + "Interface",
        (_InterfaceSocket, bpy.types.NodeTreeInterfaceSocket),
        {
            "bl_idname": socket_cls.bl_idname + "Interface",
            "bl_socket_idname": socket_cls.bl_idname,
            "has_default": has_default,
            "settings": settings,
            "__annotations__": annotations,
            "__module__": __name__,
        },
    )


INTERFACE_CLASSES = [_interface_class(cls) for cls in SOCKET_CLASSES]
# module globals, so auto_load registers them
globals().update({cls.__name__: cls for cls in INTERFACE_CLASSES})

SOCKET_IDNAMES = {cls.bl_idname for cls in SOCKET_CLASSES}
