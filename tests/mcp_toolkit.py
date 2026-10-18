"""The Object Toolkit (tests/visual/scenarios/_toolkit_demo.py), built only
through MCP tool calls, the way an agent would. tests/test_example_addon.py
checks its export is the same as the snapshot.

Nodes are added in the same order as the scenario: names (and so the names
in the generated code) follow the order nodes are added.
"""

from _toolkit_demo import SCRIPT  # tests/visual/scenarios is on sys.path


def build(call):
    call(
        "set_addon",
        settings={
            "addon_name": "Object Toolkit",
            "author": "Jane Doe",
            "tagline": "Rename, place and remember selections of objects",
            "blender_version_min": [5, 0, 0],
        },
    )
    props = {
        p["name"]: p["id"]
        for p in call(
            "edit_properties",
            owner="addon",
            add=[
                {"name": "Spacing", "type": "FLOAT", "default": 2.0, "unit": "LENGTH"},
                {"name": "Axis", "type": "ENUM", "items": ["X", "Y", "Z"]},
                {"name": "Selection Set", "type": "GROUP"},
            ],
        )["properties"]
    }
    members = {
        p["name"]: p["id"]
        for p in call(
            "edit_properties",
            owner="group:Selection Set",
            add=[
                {"name": "Name", "type": "STRING", "default": "Set"},
                {"name": "Objects", "type": "STRING"},
            ],
        )["properties"]
    }
    props.update(
        {
            p["name"]: p["id"]
            for p in call(
                "edit_properties",
                owner="addon",
                add=[
                    {"name": "Sets", "type": "COLLECTION", "group": "Selection Set"},
                    {"name": "Active Set", "type": "INTEGER"},
                ],
            )["properties"]
        }
    )
    call("write_text", text="toolkit_helpers.py", content=SCRIPT)
    call("edit_scripts", add=[{"text": "toolkit_helpers.py"}])
    describe(call)
    ops = operators(call, props, members)
    interface(call, props, members, ops)
    logic(call, props)


def describe(call):
    call("create_tree", name="Describe")
    call(
        "edit_function",
        tree="Describe",
        add=[
            {"name": "Object", "type": "Data"},
            {"name": "Text", "type": "String", "output": True},
        ],
    )
    data = {"path_root": "INPUT"}
    call(
        "edit_tree",
        tree="Describe",
        add=[
            {
                "ref": "name",
                "type": "SNA_Node_BlendData",
                "props": {**data, "path": "name"},
            },
            {
                "ref": "kind",
                "type": "SNA_Node_BlendData",
                "props": {**data, "path": "type"},
            },
            {
                "ref": "text",
                "type": "SNA_Node_FormatString",
                "inputs": {"format": "{} ({})"},
            },
        ],
        link=[
            ["Group Input.Object", "name.data"],
            ["Group Input.Object", "kind.data"],
            ["name.value", "text.value+"],
            ["kind.value", "text.value+"],
            ["text.string", "Group Output.Text"],
        ],
    )


def operators(call, props, members):
    call("create_tree", name="Operators")

    def edit(**kwargs):
        return call("edit_tree", tree="Operators", **kwargs)

    def operator(label, description, **settings):
        return {
            "type": "SNA_Node_Operator",
            "inputs": {"label": label},
            "props": {"operator_description": description, **settings},
        }

    def op_props(op, add):
        return {
            p["name"]: p["id"]
            for p in call("edit_properties", owner=op, add=add)["properties"]
        }

    # Rename Selected
    ids = edit(
        add=[
            {
                "ref": "selected",
                "type": "SNA_Node_BlendData",
                "props": {"path": "selected_objects"},
            },
            {
                "ref": "rename",
                **operator(
                    "Rename Selected",
                    "Rename the selected objects with a prefix and a number",
                    invoke_type="PROPS_DIALOG",
                ),
            },
        ]
    )["added"]
    selected, rename = ids["selected"], ids["rename"]
    op_props(
        rename,
        [
            {"name": "Prefix", "type": "STRING", "default": "Object"},
            {"name": "Start", "type": "INTEGER", "default": 1},
        ],
    )
    edit(
        add=[
            {"ref": "loop", "type": "SNA_Node_ForEachList"},
            {"ref": "number", "type": "SNA_Node_Math", "props": {"operation": "ADD"}},
            {
                "ref": "new_name",
                "type": "SNA_Node_FormatString",
                "inputs": {"format": "{}_{:03}"},
            },
            {
                "ref": "set_name",
                "type": "SNA_Node_SetAttribute",
                "inputs": {"name": "name"},
            },
            {"ref": "count", "type": "SNA_Node_ListLength"},
            {
                "ref": "message",
                "type": "SNA_Node_FormatString",
                "inputs": {"format": "Renamed {} objects"},
            },
            {"ref": "done", "type": "SNA_Node_Report"},
        ],
        link=[
            [f"{selected}.value", "loop.list"],
            ["loop.index", "number.a"],
            [f"{rename}.Start", "number.b"],
            [f"{rename}.Prefix", "new_name.value+"],
            ["number.int", "new_name.value+"],
            ["loop.item", "set_name.data"],
            ["new_name.string", "set_name.value"],
            [f"{rename}.execute", "loop.flow"],
            ["loop.loop", "set_name.flow"],
            [f"{selected}.value", "count.list"],
            ["count.length", "message.value+"],
            ["message.string", "done.message"],
            ["loop.next", "done.flow"],
        ],
    )

    # Distribute
    switches = []
    for name in "XYZ":
        switches += [
            {"ref": f"is_{name}", "type": "SNA_Node_Compare"},
            {
                "ref": f"name_{name}",
                "type": "SNA_Node_String",
                "props": {"value": name},
            },
            {
                "ref": f"choose_{name}",
                "type": "SNA_Node_SwitchData",
                "props": {"data_type": "ScriptingFloatSocket"},
            },
        ]
    get = "SNA_Node_GetProperty"
    ids = edit(
        add=[
            {
                "ref": "distribute",
                **operator("Distribute", "Place the selected objects in a line"),
            },
            {"ref": "loop", "type": "SNA_Node_ForEachList"},
            {"ref": "spacing", "type": get, "props": {"prop": props["Spacing"]}},
            {"ref": "axis", "type": get, "props": {"prop": props["Axis"]}},
            {
                "ref": "offset",
                "type": "SNA_Node_Math",
                "props": {"operation": "MULTIPLY"},
            },
            *switches,
            {"ref": "vector", "type": "SNA_Node_CombineVector"},
            {
                "ref": "set_location",
                "type": "SNA_Node_SetAttribute",
                "inputs": {"name": "location"},
            },
        ],
        link=[
            [f"{selected}.value", "loop.list"],
            ["loop.index", "offset.a"],
            ["spacing.value", "offset.b"],
            *[
                link
                for name in "XYZ"
                for link in (
                    ["axis.value", f"is_{name}.a"],
                    [f"name_{name}.value", f"is_{name}.b"],
                    [f"is_{name}.result", f"choose_{name}.condition"],
                    ["offset.result", f"choose_{name}.true"],
                )
            ],
            *[[f"choose_{n}.result", f"vector.{n.lower()}"] for n in "XYZ"],
            ["loop.item", "set_location.data"],
            ["vector.vector", "set_location.value"],
            ["distribute.execute", "loop.flow"],
            ["loop.loop", "set_location.flow"],
        ],
    )["added"]
    distribute = ids["distribute"]

    # Save Selection Set
    save = edit(
        add=[
            {
                "ref": "save",
                **operator(
                    "Save Selection Set",
                    "Remember the selected objects as a set",
                    invoke_type="PROPS_DIALOG",
                ),
            }
        ]
    )["added"]["save"]
    op_props(save, [{"name": "Name", "type": "STRING", "default": "Set"}])
    ids = edit(
        add=[
            {
                "ref": "names",
                "type": "SNA_Node_PythonExpression",
                "props": {"code": "[obj.name for obj in objects]"},
            },
            {
                "ref": "joined",
                "type": "SNA_Node_JoinList",
                "inputs": {"separator": ","},
            },
            {"ref": "sets", "type": get, "props": {"prop": props["Sets"]}},
            {"ref": "add", "type": "SNA_Node_CollectionAdd"},
            {
                "ref": "store_name",
                "type": "SNA_Node_SetProperty",
                "props": {"prop": members["Name"]},
            },
            {
                "ref": "store_objects",
                "type": "SNA_Node_SetProperty",
                "props": {"prop": members["Objects"]},
            },
        ],
        link=[
            [f"{selected}.value", "names.objects"],
            ["names.result", "joined.list"],
            ["sets.value", "add.collection"],
            ["add.new_item", "store_name.data"],
            [f"{save}.Name", "store_name.value"],
            ["add.new_item", "store_objects.data"],
            ["joined.string", "store_objects.value"],
            [f"{save}.execute", "add.flow"],
            ["add.next", "store_name.flow"],
            ["store_name.next", "store_objects.flow"],
        ],
    )["added"]
    names, sets = ids["names"], ids["sets"]

    # Restore Selection Set
    restore = edit(
        add=[
            {
                "ref": "restore",
                **operator(
                    "Restore Selection Set", "Select the objects of the active set"
                ),
            },
            {"ref": "active", "type": get, "props": {"prop": props["Active Set"]}},
            {"ref": "item", "type": "SNA_Node_CollectionGetItem"},
            {"ref": "stored", "type": get, "props": {"prop": members["Objects"]}},
            {
                "ref": "select",
                "type": "SNA_Node_ScriptFunction",
                "props": {
                    "script": "toolkit_helpers.py",
                    "function": "select_objects",
                },
            },
            {
                "ref": "found",
                "type": "SNA_Node_FormatString",
                "inputs": {"format": "Selected {} objects"},
            },
            {"ref": "done", "type": "SNA_Node_Report"},
        ],
        link=[
            [f"{sets}.value", "item.collection"],
            ["active.value", "item.index"],
            ["item.item", "stored.data"],
            ["stored.value", "select.names"],
            ["select.output_0", "found.value+"],
            ["found.string", "done.message"],
            ["restore.execute", "select.flow"],
            ["select.next", "done.flow"],
        ],
    )["added"]["restore"]

    # Export Names
    export = edit(
        add=[
            {
                "ref": "export",
                **operator(
                    "Export Names",
                    "Write the names of the selected objects to a file",
                    invoke_type="FILE_BROWSER",
                    file_mode="SAVE_FILE",
                    file_filter="*.txt",
                ),
            },
            {
                "ref": "lines",
                "type": "SNA_Node_JoinList",
                "inputs": {"separator": "\n"},
            },
            {"ref": "write", "type": "SNA_Node_WriteTextFile"},
            {
                "ref": "written",
                "type": "SNA_Node_FormatString",
                "inputs": {"format": "Wrote {}"},
            },
            {"ref": "done", "type": "SNA_Node_Report"},
        ],
        link=[
            [f"{names}.result", "lines.list"],
            ["export.path", "write.path"],
            ["lines.string", "write.text"],
            ["export.path", "written.value+"],
            ["written.string", "done.message"],
            ["export.execute", "write.flow"],
            ["write.next", "done.flow"],
        ],
    )["added"]["export"]

    # Measure (modal)
    measure = edit(
        add=[
            {
                "ref": "measure",
                **operator(
                    "Measure",
                    "Show the mouse position in the header",
                    invoke_type="MODAL",
                ),
            },
            {"ref": "info", "type": "SNA_Node_EventInfo"},
            {
                "ref": "position",
                "type": "SNA_Node_FormatString",
                "inputs": {"format": "Mouse: {}"},
            },
            {"ref": "header", "type": "SNA_Node_SetHeaderText"},
            {"ref": "clicked", "type": "SNA_Node_IsKey"},
            {"ref": "branch", "type": "SNA_Node_IfElse"},
            {"ref": "finish", "type": "SNA_Node_OperatorReturn"},
            {"ref": "clear", "type": "SNA_Node_SetHeaderText"},
        ],
        link=[
            ["measure.event", "info.event"],
            ["info.mouse_region", "position.value+"],
            ["position.string", "header.text"],
            ["measure.event", "clicked.event"],
            ["clicked.is_key", "branch.condition"],
            ["measure.modal", "header.flow"],
            ["header.next", "branch.flow"],
            ["branch.then", "finish.flow"],
            ["measure.end", "clear.flow"],
        ],
    )["added"]["measure"]
    return {
        "rename": rename,
        "distribute": distribute,
        "save": save,
        "restore": restore,
        "export": export,
        "measure": measure,
    }


def interface(call, props, members, ops):
    call("create_tree", name="Interface")
    get = "SNA_Node_GetProperty"

    def button(op, label=None, icon=None):
        node = {"type": "SNA_Node_Button", "props": {"operator_sn": ops[op]}}
        inputs = {}
        if label:
            inputs["label"] = label
        if icon:
            inputs["icon"] = icon
        if inputs:
            node["inputs"] = inputs
        return node

    added = call(
        "edit_tree",
        tree="Interface",
        add=[
            {
                "ref": "panel",
                "type": "SNA_Node_Panel",
                "inputs": {"label": "Object Toolkit"},
                "props": {"panel_category": "Toolkit"},
            },
            {
                "ref": "selected",
                "type": "SNA_Node_BlendData",
                "props": {"path": "selected_objects"},
            },
            {"ref": "count", "type": "SNA_Node_ListLength"},
            {
                "ref": "has_any",
                "type": "SNA_Node_Compare",
                "props": {"comparison_type": ">"},
            },
            {"ref": "zero", "type": "SNA_Node_Integer", "props": {"value": 0}},
            {"ref": "branch", "type": "SNA_Node_IfElse"},
            {
                "ref": "summary",
                "type": "SNA_Node_FormatString",
                "inputs": {"format": "{} selected"},
            },
            {
                "ref": "selected_label",
                "type": "SNA_Node_Label",
                "inputs": {"icon": "RESTRICT_SELECT_OFF"},
            },
            {
                "ref": "nothing",
                "type": "SNA_Node_Label",
                "inputs": {"text": "Nothing selected", "icon": "INFO"},
            },
            {"ref": "column", "type": "SNA_Node_Column", "inputs": {"align": True}},
            {"ref": "rename", **button("rename", icon="SORTALPHA")},
            {"ref": "distribute", **button("distribute", icon="ALIGN_JUSTIFY")},
            {
                "ref": "spacing",
                "type": "SNA_Node_NumberField",
                "props": {"prop": props["Spacing"]},
            },
            {
                "ref": "axis",
                "type": "SNA_Node_EnumMenu",
                "props": {"prop": props["Axis"], "expand": True},
            },
            {"ref": "measure", **button("measure", icon="DRIVER_DISTANCE")},
            {"ref": "sub", "type": "SNA_Node_Subpanel"},
            {
                "ref": "sub_label",
                "type": "SNA_Node_Label",
                "inputs": {"text": "Selection Sets"},
            },
            {"ref": "sets", "type": get, "props": {"prop": props["Sets"]}},
            {
                "ref": "ui_list",
                "type": "SNA_Node_UIList",
                "label": "Sets",
                "props": {"prop": props["Active Set"]},
            },
            {"ref": "item_name", "type": get, "props": {"prop": members["Name"]}},
            {
                "ref": "item_label",
                "type": "SNA_Node_Label",
                "inputs": {"icon": "GROUP"},
            },
            {"ref": "row", "type": "SNA_Node_Row"},
            {"ref": "save", **button("save", label="Save", icon="ADD")},
            {"ref": "restore", **button("restore", label="Select")},
            {"ref": "export", **button("export", icon="EXPORT")},
            {
                "ref": "active",
                "type": "SNA_Node_BlendData",
                "props": {"path": "active_object"},
            },
            {
                "ref": "describe",
                "type": "SNA_Node_Group",
                "props": {"node_tree": "Describe"},
            },
            {
                "ref": "described",
                "type": "SNA_Node_Label",
                "inputs": {"icon": "OBJECT_DATA"},
            },
            {
                "ref": "menu",
                "type": "SNA_Node_AddToMenu",
                "props": {"target": "VIEW3D_MT_object"},
            },
            {"ref": "separator", "type": "SNA_Node_Separator"},
            {"ref": "menu_rename", **button("rename")},
            {"ref": "menu_distribute", **button("distribute")},
            {"ref": "pie", "type": "SNA_Node_PieMenu", "inputs": {"label": "Toolkit"}},
            {"ref": "pie_rename", **button("rename")},
            {"ref": "pie_distribute", **button("distribute")},
            {"ref": "pie_measure", **button("measure")},
            {"ref": "pie_save", **button("save")},
            {
                "ref": "shortcut",
                "type": "SNA_Node_Shortcut",
                "props": {
                    "action": "MENU",
                    "menu": "pie",
                    "key": "Q",
                    "shift": True,
                    "keymap": "3D View",
                },
            },
            {"ref": "prefs", "type": "SNA_Node_Preferences"},
        ],
        link=[
            ["selected.value", "count.list"],
            ["count.length", "has_any.a"],
            ["zero.value", "has_any.b"],
            ["has_any.result", "branch.condition"],
            ["count.length", "summary.value+"],
            ["summary.string", "selected_label.text"],
            ["branch.then", "selected_label.flow"],
            ["branch.else", "nothing.flow"],
            ["column.content", "rename.flow"],
            ["rename.next", "distribute.flow"],
            ["panel.body", "branch.flow"],
            ["branch.next", "column.flow"],
            ["column.next", "spacing.flow"],
            ["spacing.next", "axis.flow"],
            ["axis.next", "measure.flow"],
            ["measure.next", "sub.flow"],
            ["sub.header", "sub_label.flow"],
            ["sets.value", "ui_list.items"],
            ["ui_list.item_data", "item_name.data"],
            ["item_name.value", "item_label.text"],
            ["ui_list.item", "item_label.flow"],
            ["row.content", "save.flow"],
            ["save.next", "restore.flow"],
            ["sub.content", "ui_list.flow"],
            ["ui_list.next", "row.flow"],
            ["row.next", "export.flow"],
            ["active.value", "describe.Object"],
            ["describe.Text", "described.text"],
            ["sub.next", "described.flow"],
            ["menu.draw", "separator.flow"],
            ["separator.next", "menu_rename.flow"],
            ["menu_rename.next", "menu_distribute.flow"],
            ["pie.left", "pie_rename.flow"],
            ["pie.right", "pie_distribute.flow"],
            ["pie.top", "pie_measure.flow"],
            ["pie.bottom", "pie_save.flow"],
        ],
    )["added"]
    verbose = call(
        "edit_properties",
        owner=added["prefs"],
        add=[
            {
                "name": "Verbose",
                "type": "BOOLEAN",
                "description": "Print what the add-on does",
            }
        ],
    )["properties"][0]["id"]
    call(
        "edit_tree",
        tree="Interface",
        add=[
            {"ref": "checkbox", "type": "SNA_Node_Checkbox", "props": {"prop": verbose}}
        ],
        link=[[f"{added['prefs']}.draw", "checkbox.flow"]],
    )


def logic(call, props):
    call("create_tree", name="Logic")
    call(
        "edit_tree",
        tree="Logic",
        add=[
            {"ref": "loaded", "type": "SNA_Node_OnLoad"},
            {
                "ref": "name",
                "type": "SNA_Node_BlendData",
                "props": {"path_root": "DATA", "path": "filepath"},
            },
            {
                "ref": "message",
                "type": "SNA_Node_FormatString",
                "inputs": {"format": "Object Toolkit: loaded {}"},
            },
            {"ref": "say", "type": "SNA_Node_Print"},
            {
                "ref": "changed",
                "type": "SNA_Node_OnPropertyUpdate",
                "props": {"prop": props["Spacing"]},
            },
            {
                "ref": "redraw",
                "type": "SNA_Node_Redraw",
                "props": {"area_type": "VIEW_3D"},
            },
        ],
        link=[
            ["name.value", "message.value+"],
            ["message.string", "say.text"],
            ["loaded.flow", "say.flow"],
            ["changed.flow", "redraw.flow"],
        ],
    )
