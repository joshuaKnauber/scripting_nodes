import bpy


class SNA_DevSettings(bpy.types.PropertyGroup):

    log_tree_rebuilds: bpy.props.BoolProperty(
        name="Log Tree Rebuilds",
        description=(
            "For each dirty tree: log node count, codegen time, and whether the "
            "file was actually written (i.e. content differed) or skipped"
        ),
        default=False,
    )

    log_reload_times: bpy.props.BoolProperty(
        name="Log Reload Times",
        description=(
            "Log each addon reload: smart (per-module) or full, which trees + "
            "dependents reloaded, codegen vs reload time"
        ),
        default=False,
    )

    show_node_code: bpy.props.BoolProperty(
        name="Show Node Code",
        description="Show the generated code of the nodes",
        default=False,
    )

    show_log_overlay: bpy.props.BoolProperty(
        name="Log Overlay",
        description="Show console logs overlaid in the node editor",
        default=True,
    )

    log_overlay_font_size: bpy.props.IntProperty(
        name="Overlay Font Size",
        description="Font size for the log overlay",
        default=18,
        min=10,
        max=36,
    )
