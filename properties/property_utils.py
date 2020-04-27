import bpy

def error_props():
    return bpy.context.scene.sn_error_properties

def clear_error_props():
    bpy.context.scene.sn_error_properties.clear()

def add_error_prop(error_type, error_message):
    prop = bpy.context.scene.sn_error_properties.add()
    prop.error_type = error_type
    prop.error_message = error_message
    return prop

def remove_error_prop(error_property):
    if error_property in bpy.context.scene.sn_error_properties:
        bpy.context.scene.sn_error_properties.remove(error_property)