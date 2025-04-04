import bpy

owner = object()


def name_change_callback(cls):
    for ntree in bpy.data.node_groups:
        if ntree.bl_idname == "ScriptingNodesTree":
            key = (
                cls.collection_key_overwrite
                if cls.collection_key_overwrite
                else cls.bl_idname
            )
            for ref in ntree.node_collection(key).refs:
                node = ref.node
                if node and node.name != ref.name:
                    ref.name = node.name
                    node.on_node_name_change()
                    node._evaluate(bpy.context)
                    return


def subscribe_to_name_change():
    unsubscribe_from_name_change()
    for cls in bpy.types.Node.__subclasses__():
        if getattr(cls, "is_sn", False):
            subscribe_to = (cls, "name")
            bpy.msgbus.subscribe_rna(
                key=subscribe_to,
                owner=owner,
                args=(cls,),
                notify=name_change_callback,
            )


def unsubscribe_from_name_change():
    bpy.msgbus.clear_by_owner(owner)
