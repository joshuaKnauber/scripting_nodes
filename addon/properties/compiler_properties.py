import bpy
from .property_utils import get_sorted_props



def property_imperative_code():
    """ Returns the imperative code for all properties """
    props = get_sorted_props(bpy.context.scene.sn.properties.values())
    imperative = ""
    for prop in props:
        imperative += prop.imperative_code + "\n"
    return imperative


def property_register_code():
    """ Returns the register code for all properties """
    props = get_sorted_props(bpy.context.scene.sn.properties.values())
    register = ""
    for prop in props:
        register += prop.register_code + "\n"
    return register


def property_unregister_code():
    """ Returns the unregister code for all properties """
    props = get_sorted_props(bpy.context.scene.sn.properties.values())
    props.reverse()
    unregister = ""
    for prop in props:
        unregister += prop.unregister_code + "\n"
    return unregister