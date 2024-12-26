from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import has_addon
from scripting_nodes.src.features.node_tree.code_gen.generator import generate_addon
import bpy


def watch_changes():
    generate_addon()

    if bpy.context.scene.sna.addon.force_production:
        return 2
    elif has_addon():
        return 0.25
    return 1
