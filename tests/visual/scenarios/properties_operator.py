"""An Operator node's own properties, edited in the sidebar's Node tab."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _properties_demo  # noqa: E402

SIDEBAR_TAB = "Node"


def setup():
    tree, op = _properties_demo.build()
    for node in tree.nodes:
        node.select = node == op
    tree.nodes.active = op
    return tree
