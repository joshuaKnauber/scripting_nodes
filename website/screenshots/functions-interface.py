"""Inside the Greet function, with its inputs and outputs in the Group tab."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _demo  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (1500, 760)
SIDEBAR_TAB = "Group"


def setup():
    _, functions = _demo.build()
    greet = functions["Greet"]
    greet.interface.active_index = 1  # Greeting
    return greet


def after(context):
    # frame the nodes next to the sidebar, not under it
    context.preferences.system.use_region_overlap = False
