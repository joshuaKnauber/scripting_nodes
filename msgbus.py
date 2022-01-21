import bpy
from .nodes.Interface.Panel import SN_PanelNode

owner = object()



def name_change_callback(*args):
    print("name change")



def subscribe_to_name_change():
    subscribe_to = (SN_PanelNode, "name")
    bpy.msgbus.subscribe_rna(
        key=subscribe_to,
        owner=owner,
        args=(1, 2, 3),
        notify=name_change_callback,
    )



def unsubscribe_from_name_change():
    pass