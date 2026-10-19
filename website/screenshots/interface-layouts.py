"""A sidebar panel with a Split, a Grid drawing a label per object, an
expanded Enum Menu, a Text Box and a Progress ring, next to the node tree."""

import bpy
import helpers

WINDOW_SIZE = (1400, 820)
LAYOUT = "split"
SIDEBAR_TAB = "Layouts"
CROP = (0, 0, 0.815, 0.78)  # nodes and panel, not the properties editor or timeline
FRAME = "corner"


def add(tree, idname, location, **settings):
    node = helpers.add_node(tree, idname, location)
    for name, value in settings.items():
        setattr(node, name, value)
    return node


def setup():
    bpy.context.scene.sna.addon.addon_name = "Layout Demo"
    tree = helpers.new_tree("Layouts")
    blender = {"mode": "BLENDER"}
    panel = add(tree, "SNA_Node_Panel", (-1100, 200), panel_category="Layouts")
    panel.inputs["Label"].value = "Layouts"
    tabs = add(
        tree,
        "SNA_Node_EnumMenu",
        (-850, 250),
        path="scene.render.engine",
        expand=True,
        **blender,
    )
    split = add(tree, "SNA_Node_Split", (-600, 250))
    left = add(tree, "SNA_Node_Label", (-350, 400))
    left.inputs["text"].value = "Resolution"
    right = add(
        tree,
        "SNA_Node_NumberField",
        (-350, 200),
        path="scene.render.resolution_percentage",
        **blender,
    )
    right.inputs["text"].value = "%"
    grid = add(tree, "SNA_Node_Grid", (-350, -100))
    grid.inputs["Columns"].value = 2
    each = add(tree, "SNA_Node_DrawForEach", (-100, -100))
    objects = add(
        tree, "SNA_Node_BlendData", (-600, -300), path_root="DATA", path="objects"
    )
    item = add(tree, "SNA_Node_Label", (150, -150))
    icon = add(tree, "SNA_Node_IconFromData", (-100, -400))
    box = add(
        tree,
        "SNA_Node_TextField",
        (-100, 200),
        path="scene.render.filepath",
        style="TEXTBOX",
        **blender,
    )
    progress = add(tree, "SNA_Node_Progress", (150, 200), progress_type="RING")
    progress.inputs["Factor"].value = 0.7
    progress.inputs["Text"].value = "Rendering"
    helpers.flush()
    box.inputs["text"].value = "Output"
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    link(panel.outputs["Draw"], tabs.inputs[0])
    link(tabs.outputs[0], split.inputs[0])
    link(split.outputs["First"], left.inputs[0])
    link(split.outputs["Second"], right.inputs[0])
    link(split.outputs["After"], grid.inputs[0])
    link(grid.outputs["Grid"], each.inputs[0])
    link(objects.outputs[0], each.inputs["List"])
    value = each.socket("item", output=True)  # "Item" is also the flow's name
    link(each.outputs[0], item.inputs[0])
    link(value, item.inputs["text"])
    link(value, icon.inputs["Data"])
    link(icon.outputs[0], item.inputs["icon"])
    link(grid.outputs["After"], box.inputs[0])
    link(box.outputs[0], progress.inputs[0])
    return tree


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
