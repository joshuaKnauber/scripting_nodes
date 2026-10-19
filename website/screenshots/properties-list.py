"""The add-on's properties in the sidebar's Addon Data panel: the list and
the settings of the selected property (Count)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _properties  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (900, 1000)
UI_SCALE = 0.85
# the Addon Data panel of the sidebar
CROP = (0.687, 0.512, 0.972, 1)


def setup():
    tree, _ = _properties.build()
    return tree
