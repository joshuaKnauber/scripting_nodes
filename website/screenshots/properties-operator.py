"""An Operator node's own properties, edited in the sidebar's Node tab."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _properties  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (1400, 1000)
SIDEBAR_TAB = "Node"
ZOOM_OUT = 2


def setup():
    tree, op = _properties.build()
    for node in tree.nodes:
        node.select = node == op
    tree.nodes.active = op
    return tree
