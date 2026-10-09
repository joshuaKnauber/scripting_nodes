"""The add-on's properties in the sidebar's Addon Data panel."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _properties  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (1400, 1000)
ZOOM_OUT = 2


def setup():
    tree, _ = _properties.build()
    return tree
