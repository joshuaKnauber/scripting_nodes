"""Socket declarations for nodes.

Nodes list their sockets instead of creating them by hand:

    sn_inputs = [Flow(), String("text", label="Text")]
    sn_outputs = [Flow("next")]

`key` is the socket's stable identifier (what `ctx.input(key)` uses), `label`
is only what the user sees. The base node creates, removes and reorders
sockets to match the declaration and keeps links of sockets that survive (see
ScriptingBaseNode.sync_sockets).
"""

from dataclasses import dataclass, field
from typing import Any

MISSING = object()


@dataclass
class SocketSpec:
    idname: str
    key: str
    label: str = ""
    default: Any = MISSING
    # flow sockets: PROGRAM, LOGIC or INTERFACE
    kind: str | None = None
    # False removes the socket from the node UI (and drops its links)
    enabled: bool = True
    hide: bool = False
    # a group of sockets the user can add/remove ("+" socket at the end)
    dynamic: bool = False
    # extra socket attributes set on creation, e.g. {"dimension": "2"}
    attrs: dict = field(default_factory=dict)

    @property
    def display_name(self):
        if self.label:
            return self.label
        if self.kind:
            return self.kind.title()
        return self.key.replace("_", " ").title()


def _spec(idname, key, label="", default=MISSING, **kwargs):
    return SocketSpec(idname, key, label, default, **kwargs)


# -- flow -----------------------------------------------------------------


def Flow(key="flow", label="", kind="PROGRAM", **kwargs):
    """Program flow (gray). Use Logic() for entry points, Interface() for UI."""
    return SocketSpec("ScriptingFlowSocket", key, label, kind=kind, **kwargs)


def Logic(key="flow", label="", **kwargs):
    return Flow(key, label, kind="LOGIC", **kwargs)


def Interface(key="flow", label="", **kwargs):
    return Flow(key, label, kind="INTERFACE", **kwargs)


# -- data -----------------------------------------------------------------


def Data(key, label="", **kwargs):
    return _spec("ScriptingDataSocket", key, label, **kwargs)


def BlendData(key, label="", **kwargs):
    return _spec("ScriptingBlendDataSocket", key, label, **kwargs)


def String(key, label="", default=MISSING, enum_items=None, **kwargs):
    spec = _spec("ScriptingStringSocket", key, label, default, **kwargs)
    if enum_items is not None:
        spec.attrs["enum_items_data"] = enum_items
    return spec


def Boolean(key, label="", default=MISSING, **kwargs):
    return _spec("ScriptingBooleanSocket", key, label, default, **kwargs)


def Float(key, label="", default=MISSING, **kwargs):
    return _spec("ScriptingFloatSocket", key, label, default, **kwargs)


def Integer(key, label="", default=MISSING, **kwargs):
    return _spec("ScriptingIntegerSocket", key, label, default, **kwargs)


def Vector(key, label="", default=MISSING, dimension=3, **kwargs):
    spec = _spec("ScriptingVectorSocket", key, label, default, **kwargs)
    spec.attrs["dimension"] = str(dimension)
    return spec


def Color(key, label="", default=MISSING, alpha=False, **kwargs):
    spec = _spec("ScriptingColorSocket", key, label, default, **kwargs)
    spec.attrs["use_alpha"] = alpha
    return spec


def List(key, label="", **kwargs):
    return _spec("ScriptingListSocket", key, label, **kwargs)


def Socket(idname, key, label="", default=MISSING, **kwargs):
    """Any socket type by bl_idname (for types chosen at runtime)."""
    if idname == "ScriptingFlowSocket":
        return Flow(key, label, **kwargs)
    return _spec(idname, key, label, default, **kwargs)
