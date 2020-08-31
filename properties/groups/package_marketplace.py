import bpy

class ScriptingNodesMarketplace(bpy.types.PropertyGroup):

    title: bpy.props.StringProperty(name="Title")
    text: bpy.props.StringProperty(name="Text")
    price: bpy.props.StringProperty(name="Price")
    url: bpy.props.StringProperty(name="URL")