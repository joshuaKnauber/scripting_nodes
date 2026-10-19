"""Shared by the publishing screenshots: a small add-on with its metadata
filled in, and sidebar panels of the Addon panel registered open."""

import bpy
import helpers


def build():
    addon = bpy.context.scene.sna.addon
    addon.addon_name = "Render Tools"
    addon.tagline = "Quick render settings in the sidebar"
    addon.author = "Jane Doe"
    addon.email = "jane@example.com"
    addon.version = (1, 2, 0)
    addon.website = "https://example.com/render-tools"
    addon.location = "View3D > Sidebar > Render Tools"
    addon.tags = {"Render", "3D View"}
    addon.copyright = "Jane Doe"  # becomes "<this year> Jane Doe"
    addon.blender_version_min = (5, 0, 0)

    tree = helpers.new_tree("Render Tools")
    panel = helpers.add_node(tree, "SNA_Node_Panel", (-300, 0))
    panel.socket("label").value = "Render Tools"
    panel.panel_category = "Render Tools"
    label = helpers.add_node(tree, "SNA_Node_Label", (0, 0))
    label.socket("text").value = "Hello from Render Tools"
    label.socket("icon").value = "RENDER_STILL"
    helpers.link(tree, panel.outputs["body"], label.inputs[0])
    helpers.flush()
    return tree


def open_panels(*names):
    """Register the Addon panel's subpanels `names` (class names) open."""
    ui = helpers.sn("src.settings.ui.addon_panel")
    children = [
        ui.SNA_PT_Metadata_Settings,
        ui.SNA_PT_Overwrite_Settings,
        ui.SNA_PT_Export_Check,
        ui.SNA_PT_Export,
    ]
    for cls in reversed([ui.SNA_PT_Addon_Settings, *children]):
        bpy.utils.unregister_class(cls)
    for cls in [ui.SNA_PT_Addon_Settings, *children]:
        if cls.__name__ in names:
            cls.bl_options = set(cls.bl_options) - {"DEFAULT_CLOSED"}
        bpy.utils.register_class(cls)
