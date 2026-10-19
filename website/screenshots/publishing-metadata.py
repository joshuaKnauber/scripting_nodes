"""The Addon panel with Metadata open, next to the add-on's nodes."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _publishing  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (900, 900)
CROP = (0.625, 0, 1, 0.855)  # the sidebar, down to Export Addon
FRAME = "float"


def setup():
    _publishing.open_panels("SNA_PT_Metadata_Settings")
    return _publishing.build()
