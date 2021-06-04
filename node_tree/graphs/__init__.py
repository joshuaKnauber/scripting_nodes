import bpy


from . import create_graphs, graph_ui_lists


classes = [create_graphs.SN_OT_CreateAddon,
            create_graphs.SN_OT_DeleteAddon,
            create_graphs.SN_OT_CreateGraph,
            create_graphs.SN_OT_MoveGraph,
            create_graphs.SN_OT_RemoveGraph,
            create_graphs.SN_OT_AppendPopup,
            create_graphs.SN_OT_AppendGraph,
            graph_ui_lists.SN_Error,
            graph_ui_lists.SN_Print,
            graph_ui_lists.SN_Graph,
            graph_ui_lists.SN_UL_GraphList]


def register():
    global classes
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)