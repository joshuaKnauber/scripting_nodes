import bpy

owner = object()


def on_node_name_change(node_class):
    bpy.context.scene.sna.references.update_ref_names_for_node(node_class.bl_idname)


def on_ntree_name_change():
    bpy.context.scene.sna.references.update_ref_names_by_ntree()


def subscribe_to_name_change():
    unsubscribe_from_name_change()
    # node name change
    for cls in bpy.types.Node.__subclasses__():
        if getattr(cls, "is_sn_node", False):
            subscribe_to = (cls, "name")
            bpy.msgbus.subscribe_rna(
                key=subscribe_to,
                owner=owner,
                args=(cls,),
                notify=on_node_name_change,
            )
    # node tree name change
    for cls in bpy.types.NodeTree.__subclasses__():
        if getattr(cls, "is_sn_node", False):
            subscribe_to = (cls, "name")
            bpy.msgbus.subscribe_rna(
                key=subscribe_to,
                owner=owner,
                args=(),
                notify=on_ntree_name_change,
            )


def unsubscribe_from_name_change():
    bpy.msgbus.clear_by_owner(owner)
