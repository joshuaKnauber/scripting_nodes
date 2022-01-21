import bpy

owner = object()



def name_change_callback(*args):
    print("name change", args, bpy.context.copy())



def subscribe_to_name_change():
    for cls in bpy.types.Node.__subclasses__():
        if getattr(cls, "is_sn", False):
            subscribe_to = (cls, "name")
            bpy.msgbus.subscribe_rna(
                key=subscribe_to,
                owner=owner,
                args=(owner, cls),
                notify=name_change_callback,
            )



def unsubscribe_from_name_change():
    pass
    # bpy.msgbus.clear_by_handle