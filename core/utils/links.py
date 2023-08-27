import bpy


def handle_link_insert(node: bpy.types.Node, link: bpy.types.NodeLink):
    """ Called when a link is inserted """
    print("link added", node)
    bpy.app.timers.register(lambda: node.mark_dirty(), first_interval=0.01)


def handle_link_remove(node: bpy.types.Node, link: bpy.types.NodeLink):
    """ Called when a link is removed """
    print("link removed", node)
    node.mark_dirty()
