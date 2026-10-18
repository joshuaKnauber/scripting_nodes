"""Object Toolkit: a realistic, mid-sized add-on built with most node kinds.
The baseline for the generated code quality work (see TODO.md, section 1):
`scripts/example_addon.py` builds and exports it.

    add-on properties   Spacing, Axis (enum), Sets (collection of Selection Set)
    group Selection Set Name, Objects (comma separated names)
    preferences         Verbose

    operators   Rename Selected (dialog: Prefix, Start), Distribute,
                Save Selection Set (dialog: Name), Restore Selection Set
                (Index), Export Names (file browser), Measure (modal)
    interface   sidebar panel with a subpanel and a UI list, Object menu
                entries, a pie menu on Shift Q
    logic       Describe function (Object -> text), a script with a
                select_objects() function, On Load, On Property Update
"""

import bpy
import helpers

FLOW = "ScriptingFlowSocket"
STRING = "ScriptingStringSocket"
DATA = "ScriptingDataSocket"

SCRIPT = '''"""Helpers of the Object Toolkit."""

import bpy


def select_objects(names: str) -> int:
    """Select the objects named in a comma separated list."""
    count = 0
    for name in names.split(","):
        obj = bpy.context.scene.objects.get(name.strip())
        if obj is not None:
            obj.select_set(True)
            count += 1
    return count
'''


def chain(tree, start, nodes):
    """Link the flow of `nodes` one after another, starting at socket
    `start`. Returns the last node's flow output."""
    previous = start
    for node in nodes:
        helpers.link(tree, previous, node.inputs[0])
        previous = node.outputs[0]
    return previous


def text(tree, location, template, *values):
    """A Format String node: each {} in `template` is replaced by the next
    socket of `values`."""
    node = helpers.add_node(tree, "SNA_Node_FormatString", location)
    node.socket("format").value = template
    for value in values:
        helpers.flush()
        helpers.link(tree, value, [s for s in node.inputs if s.is_dynamic][0])
    helpers.flush()
    return node


def blend_data(tree, path, location, root="CONTEXT"):
    node = helpers.add_node(tree, "SNA_Node_BlendData", location)
    node.path_root = root
    node.path = path
    helpers.flush()
    return node


def operator(tree, label, location, **settings):
    node = helpers.add_node(tree, "SNA_Node_Operator", location)
    node.inputs["label"].value = label
    for name, value in settings.items():
        setattr(node, name, value)
    helpers.flush()
    return node


def button(tree, op, location, label=None, icon=None):
    node = helpers.add_node(tree, "SNA_Node_Button", location)
    helpers.flush()
    helpers.point(node, "operator_sn", op)
    if label:
        node.inputs["label"].value = label
    if icon:
        node.inputs["icon"].value = icon
    return node


def field(tree, idname, prop_id, location):
    node = helpers.add_node(tree, idname, location)
    helpers.pick_property(node, helpers.prop(prop_id))
    return node


def report(tree, message, location):
    node = helpers.add_node(tree, "SNA_Node_Report", location)
    helpers.link(tree, message, node.socket("message"))
    return node


def properties():
    """The add-on's properties; returns their ids."""
    ids = {}
    ids["spacing"] = helpers.add_property(
        "Spacing", "FLOAT", default_float=2.0, unit="LENGTH"
    ).id
    axis = helpers.add_property("Axis", "ENUM")
    axis.enum_items[0].name = "X"
    axis.enum_items[1].name = "Y"
    axis.enum_items.add().name = "Z"
    ids["axis"] = axis.id
    ids["set"] = helpers.add_property("Selection Set", "GROUP").id
    ids["set_name"] = helpers.add_property(
        "Name", "STRING", owner=helpers.prop(ids["set"]), default_string="Set"
    ).id
    ids["set_objects"] = helpers.add_property(
        "Objects", "STRING", owner=helpers.prop(ids["set"])
    ).id
    ids["sets"] = helpers.add_property("Sets", "COLLECTION").id
    helpers.prop(ids["sets"]).group_id = ids["set"]
    ids["active_set"] = helpers.add_property("Active Set", "INTEGER").id
    return ids


def describe_function():
    """Describe(Object) -> Text: "Cube (MESH)"."""
    tree, group_in, group_out = helpers.new_function(
        "Describe", inputs=[("Object", DATA)], outputs=[("Text", STRING)]
    )
    name = blend_data(tree, "name", (-100, 100), root="INPUT")
    kind = blend_data(tree, "type", (-100, -100), root="INPUT")
    helpers.link(tree, group_in.outputs[0], name.socket("data"))
    helpers.link(tree, group_in.outputs[0], kind.socket("data"))
    combined = text(tree, (100, 0), "{} ({})", name.outputs[0], kind.outputs[0])
    helpers.link(tree, combined.outputs[0], group_out.inputs[0])
    return tree


def operators(tree, ids, script):
    ops = {}
    selected = blend_data(tree, "selected_objects", (-1400, 900))

    # Rename Selected: a dialog asking for the prefix
    rename = ops["rename"] = operator(
        tree,
        "Rename Selected",
        (-1400, 1400),
        invoke_type="PROPS_DIALOG",
        operator_description="Rename the selected objects with a prefix and a number",
    )
    prefix = helpers.add_property(
        "Prefix", "STRING", owner=rename, default_string="Object"
    ).id
    start = helpers.add_property("Start", "INTEGER", owner=rename, default_int=1).id
    loop = helpers.add_node(tree, "SNA_Node_ForEachList", (-1100, 1400))
    helpers.link(tree, selected.outputs[0], loop.socket("list"))
    number = helpers.add_node(tree, "SNA_Node_Math", (-1100, 1150))
    number.operation = "ADD"
    helpers.link(tree, loop.outputs["index"], number.inputs["a"])
    helpers.link(tree, rename.outputs["prop_" + start], number.inputs["b"])
    new_name = text(
        tree,
        (-850, 1150),
        "{}_{:03}",
        rename.outputs["prop_" + prefix],
        number.outputs["int"],
    )
    set_name = helpers.add_node(tree, "SNA_Node_SetAttribute", (-600, 1400))
    set_name.socket("name").value = "name"
    helpers.link(tree, loop.outputs["item"], set_name.socket("data"))
    helpers.link(tree, new_name.outputs[0], set_name.socket("value"))
    chain(tree, rename.outputs["execute"], [loop])
    helpers.link(tree, loop.outputs["loop"], set_name.inputs[0])
    count = helpers.add_node(tree, "SNA_Node_ListLength", (-850, 1600))
    helpers.link(tree, selected.outputs[0], count.socket("list"))
    message = text(tree, (-600, 1600), "Renamed {} objects", count.outputs[0])
    done = report(tree, message.outputs[0], (-300, 1400))
    helpers.link(tree, loop.outputs["next"], done.inputs[0])

    # Distribute: spaces the selected objects along the chosen axis
    distribute = ops["distribute"] = operator(
        tree,
        "Distribute",
        (-1400, 600),
        operator_description="Place the selected objects in a line",
    )
    loop = helpers.add_node(tree, "SNA_Node_ForEachList", (-1100, 600))
    helpers.link(tree, selected.outputs[0], loop.socket("list"))
    spacing = field(tree, "SNA_Node_GetProperty", ids["spacing"], (-1400, 350))
    axis = field(tree, "SNA_Node_GetProperty", ids["axis"], (-1400, 200))
    offset = helpers.add_node(tree, "SNA_Node_Math", (-1100, 350))
    offset.operation = "MULTIPLY"
    helpers.link(tree, loop.outputs["index"], offset.inputs["a"])
    helpers.link(tree, spacing.outputs[0], offset.inputs["b"])
    axes = {}
    for i, name in enumerate("XYZ"):
        is_axis = helpers.add_node(tree, "SNA_Node_Compare", (-850, 350 - 150 * i))
        helpers.link(tree, axis.outputs[0], is_axis.inputs["a"])
        axis_name = helpers.add_node(tree, "SNA_Node_String", (-850, 250 - 150 * i))
        axis_name.value = name
        helpers.link(tree, axis_name.outputs[0], is_axis.inputs["b"])
        choose = helpers.add_node(tree, "SNA_Node_SwitchData", (-600, 350 - 150 * i))
        choose.data_type = "ScriptingFloatSocket"
        helpers.flush()
        helpers.link(tree, is_axis.outputs[0], choose.socket("condition"))
        helpers.link(tree, offset.outputs[0], choose.socket("true"))
        axes[name] = choose
    vector = helpers.add_node(tree, "SNA_Node_CombineVector", (-350, 350))
    for name, choose in axes.items():
        helpers.link(tree, choose.outputs[0], vector.socket(name.lower()))
    set_location = helpers.add_node(tree, "SNA_Node_SetAttribute", (-350, 600))
    set_location.socket("name").value = "location"
    helpers.link(tree, loop.outputs["item"], set_location.socket("data"))
    helpers.link(tree, vector.outputs[0], set_location.socket("value"))
    chain(tree, distribute.outputs["execute"], [loop])
    helpers.link(tree, loop.outputs["loop"], set_location.inputs[0])

    # Save Selection Set: stores the selected names in the Sets collection
    save = ops["save"] = operator(
        tree,
        "Save Selection Set",
        (-1400, -200),
        invoke_type="PROPS_DIALOG",
        operator_description="Remember the selected objects as a set",
    )
    set_label = helpers.add_property(
        "Name", "STRING", owner=save, default_string="Set"
    ).id
    names = helpers.add_node(tree, "SNA_Node_PythonExpression", (-1100, -450))
    names.code = "[obj.name for obj in objects]"
    helpers.flush()
    helpers.link(tree, selected.outputs[0], names.inputs["objects"])
    joined = helpers.add_node(tree, "SNA_Node_JoinList", (-850, -450))
    joined.socket("separator").value = ","
    helpers.link(tree, names.outputs[0], joined.socket("list"))
    sets = field(tree, "SNA_Node_GetProperty", ids["sets"], (-1100, -650))
    add = helpers.add_node(tree, "SNA_Node_CollectionAdd", (-1100, -200))
    helpers.link(tree, sets.outputs[0], add.socket("collection"))
    store_name = field(tree, "SNA_Node_SetProperty", ids["set_name"], (-850, -200))
    helpers.link(tree, add.outputs["new_item"], store_name.socket("data"))
    helpers.link(tree, save.outputs["prop_" + set_label], store_name.socket("value"))
    store_objects = field(
        tree, "SNA_Node_SetProperty", ids["set_objects"], (-600, -200)
    )
    helpers.link(tree, add.outputs["new_item"], store_objects.socket("data"))
    helpers.link(tree, joined.outputs[0], store_objects.socket("value"))
    chain(tree, save.outputs["execute"], [add, store_name, store_objects])

    # Restore Selection Set: selects the objects of the active set (script)
    restore = ops["restore"] = operator(
        tree,
        "Restore Selection Set",
        (-1400, -900),
        operator_description="Select the objects of the active set",
    )
    active = field(tree, "SNA_Node_GetProperty", ids["active_set"], (-1400, -1150))
    item = helpers.add_node(tree, "SNA_Node_CollectionGetItem", (-1100, -1150))
    helpers.link(tree, sets.outputs[0], item.socket("collection"))
    helpers.link(tree, active.outputs[0], item.socket("index"))
    stored = field(tree, "SNA_Node_GetProperty", ids["set_objects"], (-850, -1150))
    helpers.link(tree, item.outputs[0], stored.socket("data"))
    select = helpers.add_node(tree, "SNA_Node_ScriptFunction", (-850, -900))
    select.script_id = helpers.add_script(script).id
    select.function_name = "select_objects"
    helpers.flush()
    helpers.link(tree, stored.outputs[0], select.socket("names"))
    found = text(tree, (-600, -1150), "Selected {} objects", select.outputs[-1])
    done = report(tree, found.outputs[0], (-350, -900))
    chain(tree, restore.outputs["execute"], [select, done])

    # Export Names: writes the selected names to a text file
    export = ops["export"] = operator(
        tree,
        "Export Names",
        (-1400, -1600),
        invoke_type="FILE_BROWSER",
        file_mode="SAVE_FILE",
        file_filter="*.txt",
        operator_description="Write the names of the selected objects to a file",
    )
    lines = helpers.add_node(tree, "SNA_Node_JoinList", (-1100, -1850))
    lines.socket("separator").value = "\n"
    helpers.link(tree, names.outputs[0], lines.socket("list"))
    write = helpers.add_node(tree, "SNA_Node_WriteTextFile", (-1100, -1600))
    helpers.link(tree, export.outputs["path"], write.socket("path"))
    helpers.link(tree, lines.outputs[0], write.socket("text"))
    written = text(tree, (-850, -1850), "Wrote {}", export.outputs["path"])
    done = report(tree, written.outputs[0], (-850, -1600))
    chain(tree, export.outputs["execute"], [write, done])

    # Measure: a modal operator showing the mouse position until clicked
    measure = ops["measure"] = operator(
        tree,
        "Measure",
        (-1400, -2300),
        invoke_type="MODAL",
        operator_description="Show the mouse position in the header",
    )
    info = helpers.add_node(tree, "SNA_Node_EventInfo", (-1100, -2550))
    helpers.link(tree, measure.outputs["event"], info.socket("event"))
    position = text(tree, (-850, -2550), "Mouse: {}", info.outputs["mouse_region"])
    header = helpers.add_node(tree, "SNA_Node_SetHeaderText", (-1100, -2300))
    helpers.link(tree, position.outputs[0], header.socket("text"))
    clicked = helpers.add_node(tree, "SNA_Node_IsKey", (-850, -2750))
    helpers.link(tree, measure.outputs["event"], clicked.socket("event"))
    branch = helpers.add_node(tree, "SNA_Node_IfElse", (-850, -2300))
    helpers.link(tree, clicked.outputs[0], branch.socket("condition"))
    finish = helpers.add_node(tree, "SNA_Node_OperatorReturn", (-600, -2300))
    chain(tree, measure.outputs["modal"], [header, branch])
    helpers.link(tree, branch.outputs["then"], finish.inputs[0])
    clear = helpers.add_node(tree, "SNA_Node_SetHeaderText", (-1100, -2900))
    helpers.link(tree, measure.outputs["end"], clear.inputs[0])
    return ops


def interface(tree, ids, ops, describe):
    panel = helpers.add_node(tree, "SNA_Node_Panel", (-1400, 400))
    panel.inputs["label"].value = "Object Toolkit"
    panel.panel_category = "Toolkit"

    selected = blend_data(tree, "selected_objects", (-1400, 100))
    count = helpers.add_node(tree, "SNA_Node_ListLength", (-1150, 100))
    helpers.link(tree, selected.outputs[0], count.socket("list"))
    has_any = helpers.add_node(tree, "SNA_Node_Compare", (-900, 100))
    has_any.comparison_type = ">"
    helpers.link(tree, count.outputs[0], has_any.inputs["a"])
    zero = helpers.add_node(tree, "SNA_Node_Integer", (-1150, -50))
    zero.value = 0
    helpers.link(tree, zero.outputs[0], has_any.inputs["b"])
    branch = helpers.add_node(tree, "SNA_Node_IfElse", (-1150, 400))
    helpers.link(tree, has_any.outputs[0], branch.socket("condition"))
    summary = text(tree, (-650, 100), "{} selected", count.outputs[0])
    selected_label = helpers.add_node(tree, "SNA_Node_Label", (-900, 500))
    selected_label.inputs["icon"].value = "RESTRICT_SELECT_OFF"
    helpers.link(tree, summary.outputs[0], selected_label.socket("text"))
    helpers.link(tree, branch.outputs["then"], selected_label.inputs[0])
    nothing = helpers.add_node(tree, "SNA_Node_Label", (-900, 300))
    nothing.inputs["text"].value = "Nothing selected"
    nothing.inputs["icon"].value = "INFO"
    helpers.link(tree, branch.outputs["else"], nothing.inputs[0])

    column = helpers.add_node(tree, "SNA_Node_Column", (-650, 400))
    column.inputs["align"].value = True
    rename = button(tree, ops["rename"], (-400, 500), icon="SORTALPHA")
    distribute = button(tree, ops["distribute"], (-150, 500), icon="ALIGN_JUSTIFY")
    chain(tree, column.outputs["content"], [rename, distribute])
    spacing = field(tree, "SNA_Node_NumberField", ids["spacing"], (-400, 300))
    axis = field(tree, "SNA_Node_EnumMenu", ids["axis"], (-150, 300))
    axis.expand = True
    measure = button(tree, ops["measure"], (100, 300), icon="DRIVER_DISTANCE")
    chain(tree, panel.outputs["body"], [branch])
    chain(tree, branch.outputs["next"], [column])
    chain(tree, column.outputs["next"], [spacing, axis, measure])

    # Selection Sets subpanel with a UI list
    sub = helpers.add_node(tree, "SNA_Node_Subpanel", (350, 300))
    helpers.link(tree, measure.outputs[0], sub.inputs[0])
    sub_label = helpers.add_node(tree, "SNA_Node_Label", (600, 500))
    sub_label.inputs["text"].value = "Selection Sets"
    helpers.link(tree, sub.outputs["header"], sub_label.inputs[0])
    sets = field(tree, "SNA_Node_GetProperty", ids["sets"], (350, 0))
    ui_list = helpers.add_node(tree, "SNA_Node_UIList", (600, 300))
    ui_list.label = "Sets"
    helpers.link(tree, sets.outputs[0], ui_list.socket("items"))
    helpers.pick_property(ui_list, helpers.prop(ids["active_set"]))
    item_name = field(tree, "SNA_Node_GetProperty", ids["set_name"], (850, 0))
    helpers.link(tree, ui_list.outputs["item_data"], item_name.socket("data"))
    item_label = helpers.add_node(tree, "SNA_Node_Label", (850, 300))
    item_label.inputs["icon"].value = "GROUP"
    helpers.link(tree, item_name.outputs[0], item_label.socket("text"))
    helpers.link(tree, ui_list.outputs["item"], item_label.inputs[0])
    row = helpers.add_node(tree, "SNA_Node_Row", (850, 100))
    save = button(tree, ops["save"], (1100, 150), label="Save", icon="ADD")
    restore = button(tree, ops["restore"], (1350, 150), label="Select")
    chain(tree, row.outputs["content"], [save, restore])
    export = button(tree, ops["export"], (1100, -100), icon="EXPORT")
    chain(tree, sub.outputs["content"], [ui_list])
    chain(tree, ui_list.outputs["next"], [row])
    chain(tree, row.outputs["next"], [export])

    # active object description via the Describe function
    active = blend_data(tree, "active_object", (350, -300))
    call = helpers.call_function(tree, describe, (600, -300))
    helpers.link(tree, active.outputs[0], call.inputs[0])
    described = helpers.add_node(tree, "SNA_Node_Label", (850, -300))
    described.inputs["icon"].value = "OBJECT_DATA"
    helpers.link(tree, call.outputs[0], described.socket("text"))
    helpers.link(tree, sub.outputs["next"], described.inputs[0])

    # Object menu entries
    menu = helpers.add_node(tree, "SNA_Node_AddToMenu", (-1400, -700))
    menu.target = "VIEW3D_MT_object"
    separator = helpers.add_node(tree, "SNA_Node_Separator", (-1150, -700))
    entries = [
        button(tree, ops["rename"], (-900, -700)),
        button(tree, ops["distribute"], (-650, -700)),
    ]
    chain(tree, menu.outputs[0], [separator, *entries])

    # pie menu on Shift Q
    pie = helpers.add_node(tree, "SNA_Node_PieMenu", (-1400, -1100))
    pie.inputs["label"].value = "Toolkit"
    for key, op, x in (
        ("left", "rename", -1150),
        ("right", "distribute", -900),
        ("top", "measure", -650),
        ("bottom", "save", -400),
    ):
        entry = button(tree, ops[op], (x, -1100))
        helpers.link(tree, pie.outputs[key], entry.inputs[0])
    shortcut = helpers.add_node(tree, "SNA_Node_Shortcut", (-1400, -1500))
    shortcut.action = "MENU"
    helpers.point(shortcut, "menu", pie)
    shortcut.key = "Q"
    shortcut.shift = True
    shortcut.keymap = "3D View"

    # preferences
    prefs = helpers.add_node(tree, "SNA_Node_Preferences", (-1400, -1900))
    verbose = helpers.add_property(
        "Verbose", "BOOLEAN", owner=prefs, description="Print what the add-on does"
    ).id
    helpers.flush()
    checkbox = helpers.add_node(tree, "SNA_Node_Checkbox", (-1150, -1900))
    helpers.pick_property(checkbox, helpers.prop(verbose))
    helpers.link(tree, prefs.outputs[0], checkbox.inputs[0])
    return panel


def logic(tree, ids):
    loaded = helpers.add_node(tree, "SNA_Node_OnLoad", (-600, 300))
    name = blend_data(tree, "filepath", (-600, 100), root="DATA")
    message = text(tree, (-350, 100), "Object Toolkit: loaded {}", name.outputs[0])
    say = helpers.add_node(tree, "SNA_Node_Print", (-350, 300))
    helpers.link(tree, message.outputs[0], say.socket("text"))
    helpers.link(tree, loaded.outputs[0], say.inputs[0])

    changed = helpers.add_node(tree, "SNA_Node_OnPropertyUpdate", (-600, -300))
    helpers.pick_property(changed, helpers.prop(ids["spacing"]))
    redraw = helpers.add_node(tree, "SNA_Node_Redraw", (-350, -300))
    redraw.area_type = "VIEW_3D"
    helpers.link(tree, changed.outputs[0], redraw.inputs[0])


def build():
    addon = bpy.context.scene.sna.addon
    addon.addon_name = "Object Toolkit"
    addon.author = "Jane Doe"
    addon.tagline = "Rename, place and remember selections of objects"
    addon.blender_version_min = (5, 0, 0)  # the same snapshot in every Blender
    ids = properties()
    script = bpy.data.texts.new("toolkit_helpers.py")
    script.write(SCRIPT)
    describe = describe_function()
    ops_tree = helpers.new_tree("Operators")
    ops = operators(ops_tree, ids, script)
    ui_tree = helpers.new_tree("Interface")
    interface(ui_tree, ids, ops, describe)
    logic_tree = helpers.new_tree("Logic")
    logic(logic_tree, ids)
    helpers.flush()
    return {"Operators": ops_tree, "Interface": ui_tree, "Logic": logic_tree}
