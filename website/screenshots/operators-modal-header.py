"""The Scrub Frames modal operator running in the 3D Viewport: its text
shows at the top of the viewport."""

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _operators_common import invoke_in, later  # noqa: E402

WINDOW_SIZE = (1100, 500)
AREA_ONLY = True
CROP = (0, 0, 0.75, 0.35)
FRAME = "corner"

_state = {}


def _modal_scenario():
    spec = importlib.util.spec_from_file_location(
        "operators_modal", os.path.join(HERE, "operators-modal.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def setup():
    _, op = _modal_scenario().build()
    _state["op"] = op.operator_idname
    return None  # keep the 3D Viewport


def after(context):
    invoke_in(context, "VIEW_3D", _state["op"], mouse=(0.5, 0.5), delay=1.0)
    later(_redraw, 2.0)


def _redraw():
    """The header text only shows once the area redraws."""
    import bpy

    for area in bpy.context.window_manager.windows[0].screen.areas:
        area.tag_redraw()
