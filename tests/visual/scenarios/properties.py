"""Property lists: the Addon Data sidebar with the add-on's properties next to
the panel they're drawn in."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _properties_demo  # noqa: E402

LAYOUT = "split"


def setup():
    tree, _ = _properties_demo.build()
    return tree
