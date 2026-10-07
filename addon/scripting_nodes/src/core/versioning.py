"""Upgrade node trees saved by older versions of Scripting Nodes.

Every tree stores the data version it was last saved with
(`ScriptingNodeTree.data_version`). On load, each step from that version up to
`DATA_VERSION` runs in order. Add a new step whenever saved data changes shape
(renamed properties, bl_idnames, socket identifiers, enum items, ...).
"""

from ..lib.logger import log

DATA_VERSION = 1

# data version -> function(tree) bringing a tree from version - 1 to it
STEPS = {}


def upgrade(trees):
    for tree in trees:
        version = tree.data_version
        if version >= DATA_VERSION:
            continue
        for step in range(version + 1, DATA_VERSION + 1):
            try:
                STEPS[step](tree)
            except Exception as exc:
                log("ERROR", f"Upgrading '{tree.name}' to data version {step}: {exc}")
        tree.data_version = DATA_VERSION
