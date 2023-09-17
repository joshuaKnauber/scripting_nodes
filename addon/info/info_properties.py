import bpy


class SN_AddonInfoProperties(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(default="New Addon", name="Name", description="The name of the addon")

    description: bpy.props.StringProperty(default="", name="Description", description="The description of the addon")

    use_custom_module_name: bpy.props.BoolProperty(default=False, name="Use Custom Identifier", description="Use a custom identifier for the addon")

    module_name: bpy.props.StringProperty(default="new_addon", name="Addon Identifier", description="The identifier of the addon")

    use_custom_shorthand: bpy.props.BoolProperty(default=False, name="Use Custom Shorthand", description="Use a custom shorthand for the addon")

    shorthand: bpy.props.StringProperty(default="SNA", name="Addon Shorthand", description="The shorthand of the addon")

    persist_sessions: bpy.props.BoolProperty(default=False, name="Persist Addon", description="Keep the addon installed across blender sessions")
