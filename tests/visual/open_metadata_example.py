"""Opens GUI Blender to try the add-on metadata (run by
scripts/open_example.py tests/visual/open_metadata_example.py).

A small add-on (a panel with a label) with its metadata filled in. The node
editor's sidebar shows the Addon panel with Metadata open; a Text Editor next
to it shows the generated blender_manifest.toml (the file on disk: reload it
from the Text menu after changing settings). The copyright is typed as a
name: the current year is added.
"""

import os
import sys
import traceback

import bpy

TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TESTS_DIR)

import helpers  # noqa: E402

OUTPUT = sys.argv[sys.argv.index("--") + 1]


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
    addon.permission_network = True
    addon.network_reason = "Downloads render presets"

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


def open_panels():
    """Addon and Metadata start closed: register them open for this session."""
    panels = helpers.sn("src.settings.ui.addon_panel")
    classes = (panels.SNA_PT_Addon_Settings, panels.SNA_PT_Metadata_Settings)
    for cls in (panels.SNA_PT_Overwrite_Settings, *reversed(classes)):
        bpy.utils.unregister_class(cls)
    for cls in (*classes, panels.SNA_PT_Overwrite_Settings):
        if cls in classes:
            cls.bl_options = set(cls.bl_options) - {"DEFAULT_CLOSED"}
        bpy.utils.register_class(cls)


def show(tree):
    window = bpy.context.window_manager.windows[0]
    view = max(window.screen.areas, key=lambda a: a.width * a.height)
    region = next(r for r in view.regions if r.type == "WINDOW")
    with bpy.context.temp_override(window=window, area=view, region=region):
        bpy.ops.screen.area_split(direction="VERTICAL", factor=0.55)
    views = sorted(
        (a for a in window.screen.areas if a.type == "VIEW_3D"), key=lambda a: a.x
    )
    nodes, text_area = views[0], views[1]
    nodes.type = "NODE_EDITOR"
    space = nodes.spaces.active
    space.tree_type = "ScriptingNodeTree"
    space.node_tree = tree
    space.show_region_ui = True
    for region in nodes.regions:
        if region.type == "UI":
            try:  # read-only in Blender 5.2
                region.active_panel_category = "Scripting Nodes"
            except AttributeError:
                pass

    runtime = helpers.sn("src.core.runtime")
    module = bpy.context.scene.sna.addon.module_name
    manifest = os.path.join(runtime.folder(module), "blender_manifest.toml")
    text_area.type = "TEXT_EDITOR"
    text_area.spaces.active.text = bpy.data.texts.load(manifest)
    return window, nodes


def frame_all(window, area):
    region = next(r for r in area.regions if r.type == "WINDOW")
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.ops.node.view_all()


def start():
    try:
        helpers.enable_addon()
        open_panels()
        tree = build()
        window, area = show(tree)
        bpy.app.timers.register(lambda: frame_all(window, area), first_interval=0.5)
        bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
        print("ADDON ERROR", helpers.sn("src.core.errors").addon_error, flush=True)
        print("EXAMPLE READY", OUTPUT, flush=True)
    except Exception:
        traceback.print_exc()
        print("EXAMPLE FAILED", flush=True)


bpy.app.timers.register(start, first_interval=0.5)
