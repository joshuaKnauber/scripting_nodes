"""The MCP tools, called the way a client calls them (server._run_tool on
the main thread, JSON in and out)."""

import json
import unittest

import bpy
import helpers


def call(tool, /, **arguments):
    """Call a tool like the server does; ToolErrors raise."""
    server = helpers.sn("src.mcp_server.server")
    spec = server.TOOLS[tool]
    result = server._run_tool(spec["fn"], arguments, tool, spec["writes"])
    while isinstance(result, server.Later):
        result = result.then()
    json.dumps(result, default=str)  # must be JSON
    return result


def tool_error():
    return helpers.sn("src.mcp_server.tools._common").ToolError


class MCPToolsTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()
        bpy.context.scene.sna.addon.addon_name = "Agent Test"

    def tearDown(self):
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()

    def test_tools_have_schemas(self):
        tools = helpers.sn("src.mcp_server.tools").TOOLS
        self.assertGreaterEqual(len(tools), 20)
        for name, spec in tools.items():
            self.assertTrue(spec["description"], name)
            self.assertEqual(spec["inputSchema"]["type"], "object", name)

    def test_build_and_run_an_operator(self):
        call("create_tree", name="Main")
        result = call(
            "edit_tree",
            tree="Main",
            add=[
                {"ref": "op", "type": "SNA_Node_Operator", "inputs": {"label": "Hi"}},
                {
                    "ref": "text",
                    "type": "SNA_Node_FormatString",
                    "inputs": {"format": "n={}"},
                },
                {"ref": "n", "type": "SNA_Node_Integer", "props": {"value": 7}},
                {"ref": "print", "type": "SNA_Node_Print"},
            ],
            link=[
                ["op.execute", "print.flow"],
                ["n.value", "text.value+"],
                ["text.string", "print.text"],
            ],
        )
        self.assertEqual(set(result["added"]), {"op", "text", "n", "print"})
        problems = call("get_problems", check_export=False)
        self.assertEqual(problems, {})
        code = call("get_code", tree="Main")["files"]["main.py"]
        self.assertIn('f"n={7}"', code)
        ran = call("run_operator", idname="agent_test.hi")
        self.assertEqual(ran["result"], ["FINISHED"])
        self.assertIn("n=7", ran["output"])

    def test_errors_tell_what_to_do(self):
        call("create_tree", name="Main")
        with self.assertRaises(tool_error()) as caught:
            call("edit_tree", tree="Main", add=[{"type": "SNA_Node_Nope"}])
        self.assertIn("list_node_types", str(caught.exception))
        call("edit_tree", tree="Main", add=[{"ref": "p", "type": "SNA_Node_Print"}])
        with self.assertRaises(tool_error()) as caught:
            call(
                "edit_tree",
                tree="Main",
                edit=[{"node": "Print", "inputs": {"nope": 1}}],
            )
        self.assertIn("'text'", str(caught.exception))  # lists the keys

    def test_node_needing_setup_shows_its_problem(self):
        call("create_tree", name="Main")
        added = call(
            "edit_tree",
            tree="Main",
            add=[
                {"ref": "b", "type": "SNA_Node_Button"},
                {"ref": "p", "type": "SNA_Node_Panel"},
            ],
            link=[["p.body", "b.flow"]],
        )["nodes"][0]
        self.assertEqual(added["error"], "Pick an operator")
        problems = call("get_problems", check_export=False)["nodes"]
        self.assertEqual(problems[0]["node"], added["id"])

    def test_references_and_property_pickers(self):
        call("create_tree", name="Main")
        call(
            "edit_properties",
            owner="addon",
            add=[{"name": "Count", "type": "INTEGER", "default": 3}],
        )
        result = call(
            "edit_tree",
            tree="Main",
            add=[
                {"ref": "op", "type": "SNA_Node_Operator", "inputs": {"label": "Go"}},
                {"ref": "panel", "type": "SNA_Node_Panel"},
                {
                    "ref": "button",
                    "type": "SNA_Node_Button",
                    "props": {"operator_sn": "op"},
                },
                {
                    "ref": "field",
                    "type": "SNA_Node_NumberField",
                    "props": {"prop": "Count"},
                },
            ],
            link=[["panel.body", "field.flow"], ["field.next", "button.flow"]],
        )
        self.assertTrue(all("error" not in n for n in result["nodes"]), result)
        code = call("get_code", tree="Main")["files"]["main.py"]
        self.assertIn("self.layout.prop(context.scene.agent_test, 'count')", code)
        self.assertIn("self.layout.operator('agent_test.go')", code)
        node = call("get_node", node=result["added"]["op"])
        self.assertEqual(node["used_by"][0]["node"], result["added"]["button"])

    def test_properties_groups_and_operator_lists(self):
        call("edit_properties", owner="addon", add=[{"name": "Item", "type": "GROUP"}])
        call(
            "edit_properties",
            owner="group:Item",
            add=[{"name": "Label", "type": "STRING", "default": "x"}],
        )
        listed = call(
            "edit_properties",
            owner="addon",
            add=[
                {"name": "Entries", "type": "COLLECTION", "group": "Item"},
                {"name": "Mode", "type": "ENUM", "items": ["Fast", "Precise"]},
            ],
        )["properties"]
        self.assertEqual([p["name"] for p in listed], ["Item", "Entries", "Mode"])
        call("create_tree", name="Main")
        op = call(
            "edit_tree", tree="Main", add=[{"ref": "op", "type": "SNA_Node_Operator"}]
        )["added"]["op"]
        call("edit_properties", owner=op, add=[{"name": "Amount", "type": "FLOAT"}])
        files = call("get_code")["files"]
        self.assertIn(
            "entries: bpy.props.CollectionProperty(name='Entries'",
            files["properties.py"],
        )
        self.assertIn("('Precise', 'Precise', '')", files["properties.py"])
        self.assertIn(
            "amount: bpy.props.FloatProperty(name='Amount')", files["main.py"]
        )
        renamed = call(
            "edit_properties",
            owner="addon",
            edit=[{"property": "Mode", "name": "Speed"}],
        )
        self.assertIn("Speed", [p["name"] for p in renamed["properties"]])

    def test_functions(self):
        call("create_tree", name="Double")
        result = call(
            "edit_function",
            tree="Double",
            add=[
                {"name": "Value", "type": "Float"},
                {"name": "Result", "type": "Float", "output": True},
            ],
        )
        self.assertEqual(result["function"], "double")
        call(
            "edit_tree",
            tree="Double",
            add=[
                {
                    "ref": "m",
                    "type": "SNA_Node_Math",
                    "props": {"operation": "MULTIPLY"},
                    "inputs": {"b": 2},
                }
            ],
            link=[["Group Input.Value", "m.a"], ["m.result", "Group Output.Result"]],
        )
        code = call("get_code", tree="Double")["files"]["double.py"]
        self.assertIn("def double(value):\n    return value * 2.0", code)
        call("create_tree", name="Main")
        call(
            "edit_tree",
            tree="Main",
            add=[
                {"ref": "g", "type": "SNA_Node_Group", "props": {"node_tree": "Double"}}
            ],
        )
        self.assertEqual(call("get_problems", check_export=False), {})

    def test_blend_data_paths(self):
        found = call("search_data_paths", query="render fps")["paths"]
        self.assertIn("bpy.context.scene.render.fps", [p["path"] for p in found])
        call("create_tree", name="Main")
        node = call(
            "edit_tree",
            tree="Main",
            add=[
                {
                    "type": "SNA_Node_BlendData",
                    "props": {"paste_path": "bpy.context.scene.render.fps"},
                }
            ],
        )["nodes"][0]
        self.assertEqual(node["outputs"][0]["type"], "Integer")

    def test_addon_settings_and_export(self):
        call(
            "set_addon",
            settings={
                "author": "Agent",
                "tagline": "Made by an agent",
                "version": [1, 2, 0],
            },
        )
        overview = call("get_addon")
        self.assertEqual(overview["metadata"]["author"], "Agent")
        with self.assertRaises(tool_error()):
            call("set_addon", settings={"colour": "red"})
        call("create_tree", name="Main")
        call("edit_tree", tree="Main", add=[{"type": "SNA_Node_Operator"}])
        import tempfile

        path = tempfile.mktemp(suffix=".zip")
        exported = call("export_addon", filepath=path)
        self.assertIn("__init__.py", exported["files"])
        self.assertEqual(exported["issues"], [])

    def test_texts_and_script_node(self):
        call(
            "write_text",
            text="tools.py",
            content="def double(x: float) -> float:\n    return x * 2\n",
        )
        scripts = call("edit_scripts", add=[{"text": "tools.py"}])["scripts"]
        self.assertEqual(
            scripts,
            [{"script": "tools.py", "folder": "Scripts", "functions": ["double"]}],
        )
        call("create_tree", name="Main")
        node = call(
            "edit_tree",
            tree="Main",
            add=[
                {
                    "type": "SNA_Node_ScriptFunction",
                    "props": {"script": "tools.py", "function": "double"},
                },
            ],
        )["nodes"][0]
        self.assertIn("x", [s["key"] for s in node["inputs"]])
        read = call("read_text", node=node["id"])
        self.assertIn("return x * 2", read["content"])
        call("write_text", text="tools.py", replace={"old": "x * 2", "new": "x * 3"})
        self.assertIn("x * 3", call("read_text", text="tools.py")["content"])

    def test_run_python(self):
        first = call("run_python", code="value = 21\nvalue * 2")
        self.assertEqual(first["result"], "42")
        printed = call("run_python", code="print(value, bpy.app.version >= (5, 0, 0))")
        self.assertEqual(printed["output"], "21 True\n")
        failed = call("run_python", code="1 / 0")
        self.assertIn("ZeroDivisionError", failed["error"])
        prefs = helpers.sn("src.settings.preferences").get_preferences()
        prefs.mcp_allow_python = False
        try:
            with self.assertRaises(tool_error()):
                call("run_python", code="1")
        finally:
            prefs.mcp_allow_python = True

    def test_screenshot_needs_a_window(self):
        with self.assertRaises(tool_error()):
            call("screenshot")

    def test_making_groups_needs_a_window(self):
        call("create_tree", name="Main")
        node = call("edit_tree", tree="Main", add=[{"type": "SNA_Node_Math"}])
        with self.assertRaises(tool_error()) as caught:
            call("make_group", tree="Main", nodes=[node["nodes"][0]["id"]])
        self.assertIn("window", str(caught.exception))  # tests/gui/mcp.py
