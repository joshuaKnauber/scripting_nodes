"""Opens GUI Blender to try icons (run by
scripts/open_example.py tests/visual/open_icons_example.py).

One panel ("Icons" tab of the 3D viewport sidebar) using every way to get an
icon: picked on the socket, the Icon node, a Custom Icon from a packed image,
an icon name from a String, icons on a button, fields, a menu, a subpanel
header, enum items listed with a property and enum items from a function
(Enum Item nodes, one with the custom icon).
"""

import os
import sys
import tempfile
import traceback

import bpy

TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TESTS_DIR)

import helpers  # noqa: E402

OUTPUT = sys.argv[sys.argv.index("--") + 1]


def logo():
    """A packed 64px image: an orange ring with a dot."""
    size = 64
    image = bpy.data.images.new("Logo", size, size, alpha=True)
    pixels = []
    for y in range(size):
        for x in range(size):
            d = ((x - 31.5) ** 2 + (y - 31.5) ** 2) ** 0.5
            if d < 9 or 19 < d < 29:
                pixels += [1.0, 0.45, 0.1, 1.0]
            else:
                pixels += [0.0, 0.0, 0.0, 0.0]
    image.pixels = pixels
    image.filepath_raw = os.path.join(tempfile.mkdtemp(), "logo.png")
    image.file_format = "PNG"
    image.save()
    image.source = "FILE"
    image.pack()
    return image


def blender_operator(idname):
    operator_call = helpers.sn("src.nodes._operator_call")
    return next(
        display
        for display, bl_idname in operator_call.blender_operator_choices()
        if bl_idname == idname
    )


def shapes_function(custom_icon_image):
    """Items function: Cube, Sphere (built-in icons) and Logo (custom)."""
    function, _, group_output = helpers.new_function(
        "Shape Items", outputs=[("Items", "ScriptingListSocket")]
    )
    create = helpers.add_node(function, "SNA_Node_CreateList", (200, 0))
    custom = helpers.add_node(function, "SNA_Node_CustomIcon", (-500, -300))
    custom.image = custom_icon_image
    for i, (name, icon) in enumerate(
        (("Cube", "MESH_CUBE"), ("Sphere", "MESH_UVSPHERE"), ("Logo", None))
    ):
        item = helpers.add_node(function, "SNA_Node_EnumItem", (-200, 200 - i * 200))
        item.name_prop = name
        item.description = f"A {name.lower()}"
        if icon:
            item.inputs["icon"].value = icon
        else:
            helpers.link(function, custom.outputs[0], item.inputs["icon"])
        helpers.link(function, item.outputs[0], create.inputs[-1])
    helpers.link(function, create.outputs["list"], group_output.inputs[0])
    group_output.location = (450, 0)
    return function


def build():
    bpy.context.scene.sna.addon.addon_name = "Icons Example"
    image = logo()

    # add-on properties: enum items with built-in icons, and from a function
    shading = helpers.add_property("Shading", "ENUM")
    shading.enum_items.clear()
    for name, icon in (
        ("Wireframe", "SHADING_WIRE"),
        ("Solid", "SHADING_SOLID"),
        ("Material", "MATERIAL"),
        ("Rendered", "SHADING_RENDERED"),
    ):
        item = shading.enum_items.add()
        item.name = name
        item.icon = icon
    shading.default_enum = "Solid"
    shape = helpers.add_property("Shape", "ENUM", items_function=shapes_function(image))

    tree = helpers.new_tree("Icons Example")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731

    panel = add("SNA_Node_Panel", -1500, 300)
    panel.socket("label").value = "Icons Example"
    panel.panel_category = "Icons"

    # header: a label with an icon (panels have no icon of their own)
    header = add("SNA_Node_Label", -1200, 600)
    header.socket("text").value = ""
    header.socket("icon").value = "FUND"
    link(panel.outputs["header"], header.inputs[0])

    # sources
    icon_node = add("SNA_Node_Icon", -1200, 50)
    icon_node.icon = "SHADING_RENDERED"
    custom = add("SNA_Node_CustomIcon", -1200, -150)
    custom.image = image
    name = add("SNA_Node_String", -1200, -450)
    name.value = "LIGHT_SUN"

    chain = []

    picked = add("SNA_Node_Label", -1200, 300)
    picked.socket("text").value = "Picked on the socket"
    picked.socket("icon").value = "MESH_MONKEY"
    chain.append(picked)

    from_node = add("SNA_Node_Label", -900, 300)
    from_node.socket("text").value = "From the Icon node"
    link(icon_node.outputs[0], from_node.socket("icon"))
    chain.append(from_node)

    from_image = add("SNA_Node_Label", -600, 300)
    from_image.socket("text").value = "Custom icon (packed image)"
    link(custom.outputs[0], from_image.socket("icon"))
    chain.append(from_image)

    from_string = add("SNA_Node_Label", -300, 300)
    from_string.socket("text").value = "Icon name from a String"
    link(name.outputs[0], from_string.socket("icon"))
    chain.append(from_string)

    button = add("SNA_Node_Button", 0, 300)
    button.mode = "BLENDER"
    button.operator_blender = blender_operator("mesh.primitive_monkey_add")
    helpers.flush()
    button.socket("label").value = "Add Monkey"
    link(custom.outputs[0], button.socket("icon"))
    chain.append(button)

    simplify = add("SNA_Node_Checkbox", -900, -750)
    simplify.mode = "BLENDER"
    simplify.path = "scene.render.use_simplify"
    simplify.toggle = True
    simplify.socket("icon").value = "MOD_DECIM"
    chain.append(simplify)

    frame_end = add("SNA_Node_NumberField", -600, -750)
    frame_end.mode = "BLENDER"
    frame_end.path = "scene.frame_end"
    frame_end.socket("icon").value = "PREVIEW_RANGE"
    chain.append(frame_end)

    shading_menu = add("SNA_Node_EnumMenu", -300, -750)
    helpers.pick_property(shading_menu, shading)
    shading_menu.expand = True
    chain.append(shading_menu)

    shape_menu = add("SNA_Node_EnumMenu", 0, -750)
    helpers.pick_property(shape_menu, shape)
    shape_menu.expand = True
    chain.append(shape_menu)

    menu = add("SNA_Node_Menu", 300, -750)
    menu.socket("label").value = "More"
    menu.socket("icon").value = "COLLAPSEMENU"
    chain.append(menu)
    in_menu = add("SNA_Node_Label", 600, -550)
    in_menu.socket("text").value = "Inside the menu"
    in_menu.socket("icon").value = "INFO"
    link(menu.outputs["content"], in_menu.inputs[0])

    subpanel = add("SNA_Node_Subpanel", 600, -800)
    link(menu.outputs["next"], subpanel.inputs[0])
    sub_header = add("SNA_Node_Label", 900, -650)
    sub_header.socket("text").value = "Subpanel"
    sub_header.socket("icon").value = "PREFERENCES"
    link(subpanel.outputs["header"], sub_header.inputs[0])
    sub_body = add("SNA_Node_Label", 900, -900)
    sub_body.socket("text").value = "Icons work anywhere a label does"
    sub_body.socket("icon").value = "CHECKMARK"
    link(subpanel.outputs["content"], sub_body.inputs[0])

    link(panel.outputs["body"], chain[0].inputs[0])
    for a, b in zip(chain, chain[1:]):
        link(a.outputs[0], b.inputs[0])
    helpers.flush()
    return tree


def show(tree):
    window = bpy.context.window_manager.windows[0]
    view = max(window.screen.areas, key=lambda a: a.width * a.height)
    region = next(r for r in view.regions if r.type == "WINDOW")
    with bpy.context.temp_override(window=window, area=view, region=region):
        bpy.ops.screen.area_split(direction="VERTICAL", factor=0.6)
    views = [a for a in window.screen.areas if a.type == "VIEW_3D"]
    nodes = min(views, key=lambda a: a.x)
    viewport = max(views, key=lambda a: a.x)
    nodes.type = "NODE_EDITOR"
    space = nodes.spaces.active
    space.tree_type = "ScriptingNodeTree"
    space.node_tree = tree
    space.show_region_ui = False
    viewport.spaces.active.show_region_ui = True
    return window, nodes, viewport


def finish(window, area, viewport):
    """Frame the tree and open the Icons tab (it exists once the add-on's
    panel is registered and drawn)."""
    region = next(r for r in area.regions if r.type == "WINDOW")
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.ops.node.view_all()
    for region in viewport.regions:
        if region.type == "UI":
            try:  # read-only in Blender 5.2
                region.active_panel_category = "Icons"
            except AttributeError:
                pass
            region.tag_redraw()


def start():
    try:
        helpers.enable_addon()
        tree = build()
        window, area, viewport = show(tree)
        bpy.app.timers.register(
            lambda: finish(window, area, viewport), first_interval=0.5
        )
        bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
        errors = helpers.sn("src.core.errors")
        print("ADDON ERROR", errors.addon_error, flush=True)
        print("NODE ERRORS", dict(errors.node_errors), flush=True)
        print("EXAMPLE READY", OUTPUT, flush=True)
    except Exception:
        traceback.print_exc()
        print("EXAMPLE FAILED", flush=True)


bpy.app.timers.register(start, first_interval=0.5)
