import bpy


class PresetData(bpy.types.PropertyGroup):
    
    name: bpy.props.StringProperty(name="Name",
                            description="Name of this preset node")

    idname: bpy.props.StringProperty(name="Idname",
                            description="The idname of this node")
    
    data: bpy.props.StringProperty(name="Data",
                            description="The stringified json data used to recreate this node")