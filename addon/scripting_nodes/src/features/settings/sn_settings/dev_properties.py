import bpy


class SNA_DevSettings(bpy.types.PropertyGroup):

    log_tree_rebuilds: bpy.props.BoolProperty(
        name="Log Tree Rebuilds",
        description="Log when a dirty node tree gets rebuilt",
        default=False,
    )

    log_reload_times: bpy.props.BoolProperty(
        name="Log Reload Times",
        description="Log the time it takes to reload the addon",
        default=False,
    )
