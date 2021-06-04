import bpy


from . import base_node, node_tree, node_categories

from . import assets, graphs, icons, libraries, snippets, sockets, variables


classes = [base_node.SN_NodePropertyGroup,
            base_node.SN_GenericPropertyGroup,
            base_node.SN_NodeCollection,
            node_tree.ScriptingNodesTree]


def register():
    global classes
    for cls in classes:
        bpy.utils.register_class(cls)

    assets.register()
    graphs.register()
    icons.register()
    libraries.register()
    snippets.register()
    sockets.register()
    variables.register()


def unregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    assets.unregister()
    graphs.unregister()
    icons.unregister()
    libraries.unregister()
    snippets.unregister()
    sockets.unregister()
    variables.unregister()