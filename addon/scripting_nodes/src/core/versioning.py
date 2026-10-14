"""Upgrade node trees saved by older versions of Scripting Nodes.

Every tree stores the data version it was last saved with
(`ScriptingNodeTree.data_version`). On load, each step from that version up to
`DATA_VERSION` runs in order. Add a new step whenever saved data changes shape
(renamed properties, bl_idnames, socket identifiers, enum items, ...).
"""

from ..lib.logger import log

DATA_VERSION = 2


def _script_functions(tree):
    """Script nodes pick the function they call (they always called run())."""
    for node in tree.nodes:
        if node.bl_idname != "SNA_Node_Script" or node.function_name:
            continue
        if "run" in node.script_functions():
            node.function_name = "run"


# data version -> function(tree) bringing a tree from version - 1 to it
STEPS = {2: _script_functions}


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
