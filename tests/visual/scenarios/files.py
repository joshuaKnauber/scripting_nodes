"""Node trees and scripts in folders: the Files list in the sidebar."""

import bpy
import helpers


def setup():
    folders = helpers.sn("src.core.folders")
    file_list = helpers.sn("src.node_tree.file_list")
    trees = {}
    for name, folder in (
        ("Main", ""),
        ("Shortcuts", ""),
        ("Object Panel", "UI/Panels"),
        ("Tool Panel", "UI/Panels"),
        ("Context Menu", "UI"),
        ("Cleanup", "Operators"),
        ("Rename Objects", "Operators"),
        ("Helpers", "Utilities"),
    ):
        trees[name] = helpers.new_tree(name)
        helpers.add_node(trees[name], "SNA_Node_Trigger")
        trees[name].folder = folder
    folders.add("Drafts")
    folders.sync()
    helpers.sn("src.core.scheduler").request_full()
    helpers.flush()
    block = bpy.data.texts.new("naming.py")
    block.write("def clean(name: str) -> str:\n    return name.strip()\n")
    script = helpers.add_script(block)
    script.folder = "Utilities"
    file_list.sync()
    file_list.select(bpy.context, "SCRIPT", script)
    return trees["Tool Panel"]
