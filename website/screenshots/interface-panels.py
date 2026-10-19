"""The Object Tools panel in the 3D Viewport's sidebar, next to its nodes."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _interface_tools  # noqa: E402

WINDOW_SIZE = (1200, 560)
LAYOUT = "split"
SIDEBAR_TAB = "Object Tools"
FRAME = "corner"
CROP = (0, 0, 0.84, 0.86)


def setup():
    tree, _ = _interface_tools.build()
    return tree


def after(context):
    _interface_tools.hide_node_sidebar(context)
