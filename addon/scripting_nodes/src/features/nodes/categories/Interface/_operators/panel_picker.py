import bpy
from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import node_by_id

# Store registered picker panels for cleanup
_picker_panels = []
_active_picker_node_id = None

# Cached enum items
_cached_space_types = None
_cached_region_types = None
_cached_context_types = None
_cached_locations = None


def _discover_panel_attributes():
    """Discover all panel attributes from registered panels and cache them."""
    global _cached_space_types, _cached_region_types, _cached_context_types, _cached_locations

    space_types = {}
    region_types = {}
    context_types = {"NONE": ("NONE", "None", "No specific context")}
    locations = {}

    # Iterate through all registered panel classes
    for name in dir(bpy.types):
        cls = getattr(bpy.types, name, None)
        if cls is None:
            continue

        # Check if it's a Panel subclass
        if not isinstance(cls, type) or not issubclass(cls, bpy.types.Panel):
            continue

        # Skip our own picker panels
        if hasattr(cls, "bl_idname") and cls.bl_idname.startswith("SNA_PT_Picker_"):
            continue

        # Get panel attributes
        space_type = getattr(cls, "bl_space_type", None)
        region_type = getattr(cls, "bl_region_type", None)
        context = getattr(cls, "bl_context", None)

        if not space_type or not region_type:
            continue

        # Collect space types
        if space_type not in space_types:
            space_name = space_type.replace("_", " ").title()
            space_types[space_type] = (space_type, space_name, f"{space_name} editor")

        # Collect region types
        if region_type not in region_types:
            region_name = region_type.replace("_", " ").title()
            region_types[region_type] = (
                region_type,
                region_name,
                f"{region_name} region",
            )

        # Collect context types
        if context and context not in context_types:
            context_name = context.replace("_", " ").title()
            context_types[context] = (context, context_name, f"{context_name} context")

        # Collect locations
        key = (space_type, region_type, context or "")
        if key not in locations:
            space_name = space_type.replace("_", " ").title()
            region_name = region_type.replace("_", " ").title()

            if context:
                context_name = context.replace("_", " ").title()
                description = f"{space_name} - {region_name} ({context_name})"
            else:
                description = f"{space_name} - {region_name}"

            locations[key] = (space_type, region_type, context, description)

    # Sort and cache
    _cached_space_types = sorted(space_types.values(), key=lambda x: x[1])
    _cached_region_types = sorted(region_types.values(), key=lambda x: x[1])
    _cached_context_types = sorted(context_types.values(), key=lambda x: x[1])
    _cached_locations = sorted(locations.values(), key=lambda x: x[3])


def get_space_type_items(self, context):
    """Get cached space type enum items."""
    global _cached_space_types
    if _cached_space_types is None:
        _discover_panel_attributes()
    return _cached_space_types


def get_region_type_items(self, context):
    """Get cached region type enum items."""
    global _cached_region_types
    if _cached_region_types is None:
        _discover_panel_attributes()
    return _cached_region_types


def get_context_type_items(self, context):
    """Get cached context type enum items."""
    global _cached_context_types
    if _cached_context_types is None:
        _discover_panel_attributes()
    return _cached_context_types


def get_panel_locations():
    """Get cached panel locations."""
    global _cached_locations
    if _cached_locations is None:
        _discover_panel_attributes()
    return _cached_locations


def invalidate_cache():
    """Invalidate the cached panel attributes (call if panels are registered/unregistered)."""
    global _cached_space_types, _cached_region_types, _cached_context_types, _cached_locations
    _cached_space_types = None
    _cached_region_types = None
    _cached_context_types = None
    _cached_locations = None


def create_picker_panel(space_type, region_type, context_type, description, index):
    """Dynamically create a picker panel class for a specific location."""

    class_name = f"SNA_PT_Picker_{index}"

    class_dict = {
        "bl_idname": f"SNA_PT_Picker_{index}",
        "bl_label": "",
        "bl_space_type": space_type,
        "bl_region_type": region_type,
        "bl_options": {"HIDE_HEADER"},
        "bl_order": 999999,  # Put at the end
        "_picker_space": space_type,
        "_picker_region": region_type,
        "_picker_context": context_type,
        "_picker_description": description,
    }

    if region_type == "UI":
        class_dict["bl_category"] = "Pick Location"

    if context_type:
        class_dict["bl_context"] = context_type

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        col.scale_y = 1.2
        col.label(text=self._picker_description, icon="RESTRICT_SELECT_OFF")
        col.alert = True
        op = col.operator(
            "sna.panel_picker_select", text="Pick This Location", icon="CHECKMARK"
        )
        op.space_type = self._picker_space
        op.region_type = self._picker_region
        op.context_type = self._picker_context if self._picker_context else "NONE"

    class_dict["draw"] = draw

    panel_class = type(class_name, (bpy.types.Panel,), class_dict)
    return panel_class


class SNA_OT_PanelPickerStart(bpy.types.Operator):
    bl_idname = "sna.panel_picker_start"
    bl_label = "Pick Panel Location"
    bl_description = (
        "Click a location in Blender's UI to set where this panel should appear"
    )
    bl_options = {"REGISTER", "INTERNAL"}

    node_id: bpy.props.StringProperty()

    def execute(self, context):
        global _picker_panels, _active_picker_node_id

        # Store the node ID
        _active_picker_node_id = self.node_id

        # Dynamically discover all panel locations from registered panels
        panel_locations = get_panel_locations()

        # Register all picker panels
        for i, (space, region, ctx, desc) in enumerate(panel_locations):
            try:
                panel_class = create_picker_panel(space, region, ctx, desc, i)
                bpy.utils.register_class(panel_class)
                _picker_panels.append(panel_class)
            except Exception as e:
                print(f"Failed to register picker panel for {desc}: {e}")

        # Force UI redraw
        for area in context.screen.areas:
            area.tag_redraw()

        self.report(
            {"INFO"}, "Click 'Pick This Location' in any area to select that location"
        )
        return {"FINISHED"}


class SNA_OT_PanelPickerSelect(bpy.types.Operator):
    bl_idname = "sna.panel_picker_select"
    bl_label = "Select This Location"
    bl_description = "Use this location for the panel"
    bl_options = {"REGISTER", "INTERNAL"}

    space_type: bpy.props.StringProperty()
    region_type: bpy.props.StringProperty()
    context_type: bpy.props.StringProperty()

    def execute(self, context):
        global _picker_panels, _active_picker_node_id

        # Update the node
        if _active_picker_node_id:
            node = node_by_id(_active_picker_node_id)
            if node:
                node.panel_space_type = self.space_type
                node.panel_region_type = self.region_type
                if self.context_type != "NONE":
                    node.panel_context = self.context_type
                else:
                    node.panel_context = "NONE"

                # Set default category for sidebar
                if self.region_type == "UI" and not node.panel_category:
                    node.panel_category = "Scripting Nodes"

        # Cleanup picker panels
        cleanup_picker_panels()

        self.report(
            {"INFO"}, f"Panel location set to {self.space_type} - {self.region_type}"
        )
        return {"FINISHED"}


class SNA_OT_PanelPickerCancel(bpy.types.Operator):
    bl_idname = "sna.panel_picker_cancel"
    bl_label = "Cancel Location Picker"
    bl_description = "Cancel the panel location picker"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        cleanup_picker_panels()
        self.report({"INFO"}, "Panel location picker cancelled")
        return {"FINISHED"}


def cleanup_picker_panels():
    """Unregister all picker panels and reset state."""
    global _picker_panels, _active_picker_node_id

    for panel_class in _picker_panels:
        try:
            bpy.utils.unregister_class(panel_class)
        except Exception as e:
            print(f"Failed to unregister picker panel: {e}")

    _picker_panels = []
    _active_picker_node_id = None

    # Force UI redraw
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()


def is_picker_active():
    """Check if the panel picker is currently active."""
    return _active_picker_node_id is not None


def get_active_picker_node_id():
    """Get the node ID of the currently active picker."""
    return _active_picker_node_id
