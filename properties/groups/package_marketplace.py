import bpy

class ScriptingNodesMarketplace(bpy.types.PropertyGroup):

    title: bpy.props.StringProperty(name="Title")
    text: bpy.props.StringProperty(name="Text")
    price: bpy.props.StringProperty(name="Price")
    url: bpy.props.StringProperty(name="URL")
    
    author: bpy.props.StringProperty(name="Author")
    category: bpy.props.StringProperty(name="Category")
    blender_version: bpy.props.IntVectorProperty(name="Blender Version")
    addon_version: bpy.props.IntVectorProperty(name="Addon Version")
    blender: bpy.props.BoolProperty(name="Blender")
    blend_url: bpy.props.StringProperty(name="Blender URL")