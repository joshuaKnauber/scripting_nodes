"""Functions (node groups): the Main tree calls three functions, the panel
they draw shows up in the 3D viewport sidebar."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _functions_demo  # noqa: E402

LAYOUT = "split"


def setup():
    tree, _ = _functions_demo.build()
    return tree
