"""The MCP server in a real Blender window, over HTTP like a client: tools
run on the main thread while it keeps drawing, screenshots, undo steps per
tool call, operators that need an editor.

Runs inside GUI Blender via `python scripts/test.py --gui`. Prints
"GUI TEST PASSED" or "GUI TEST FAILED: <reason>" and quits.
"""

import base64
import json
import os
import socket
import sys
import threading
import traceback
import urllib.request

import bpy

sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import helpers  # noqa: E402

state = {"thread": None, "results": {}, "error": None, "ticks": 0}


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def client(port):
    """The calls of an MCP client, from another thread."""
    ids = iter(range(1, 1000))

    def rpc(method, params=None):
        body = {"jsonrpc": "2.0", "id": next(ids), "method": method}
        if params is not None:
            body["params"] = params
        request = urllib.request.Request(
            f"http://127.0.0.1:{port}/",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read())["result"]

    def tool(tool_name, /, **arguments):
        result = rpc("tools/call", {"name": tool_name, "arguments": arguments})
        if result.get("isError"):
            raise AssertionError(f"{tool_name}: {result['content'][0]['text']}")
        content = result["content"]
        if content[0]["type"] == "image":
            return content
        return json.loads(content[0]["text"])

    try:
        results = state["results"]
        results["init"] = rpc("initialize", {})
        results["tools"] = [t["name"] for t in rpc("tools/list")["tools"]]
        tool("create_tree", name="Agent")
        results["added"] = tool(
            "edit_tree",
            tree="Agent",
            add=[{"ref": "op", "type": "SNA_Node_Operator", "inputs": {"label": "Hi"}}],
        )["added"]
        results["shot"] = tool("screenshot", max_size=800)
        results["area_shot"] = tool("screenshot", area="VIEW_3D", max_size=400)
        results["view"] = tool(
            "run_python",
            code="with override('VIEW_3D'):\n    bpy.ops.view3d.view_all()\nC.area",
        )
        results["ran"] = tool("run_operator", idname="mcp_gui.hi")
        tool("edit_tree", tree="Agent", add=[{"type": "SNA_Node_Print"}])
        results["undo"] = tool("undo")
        results["after_undo"] = tool("get_tree", tree="Agent")

        # a function made from nodes, and back
        tool("create_tree", name="Maths")
        added = tool(
            "edit_tree",
            tree="Maths",
            add=[
                {"ref": "op", "type": "SNA_Node_Operator", "inputs": {"label": "Sum"}},
                {"ref": "a", "type": "SNA_Node_Math", "inputs": {"a": 2, "b": 3}},
                {
                    "ref": "b",
                    "type": "SNA_Node_Math",
                    "props": {"operation": "MULTIPLY"},
                    "inputs": {"b": 2},
                },
                {"ref": "print", "type": "SNA_Node_Print"},
            ],
            link=[
                ["op.execute", "print.flow"],
                ["a.result", "b.a"],
                ["b.result", "print.text"],
            ],
        )["added"]
        results["group"] = tool(
            "make_group", tree="Maths", nodes=[added["a"], added["b"]], name="Calc"
        )
        results["group_ran"] = tool("run_operator", idname="mcp_gui.sum")
        results["group_problems"] = tool("get_problems", check_export=False)
        results["ungrouped"] = tool(
            "ungroup", node=results["group"]["group_node"]["id"]
        )
        results["after_ungroup"] = tool("get_tree", tree="Maths")
    except Exception as exc:  # noqa: BLE001 - reported by the main thread
        state["error"] = f"{type(exc).__name__}: {exc}"


def check(condition, reason):
    if not condition:
        raise AssertionError(reason)


def start():
    helpers.enable_addon()
    bpy.context.scene.sna.addon.addon_name = "MCP GUI"
    server = helpers.sn("src.mcp_server.server")
    port = free_port()
    server.start(port)
    state["thread"] = threading.Thread(target=client, args=(port,), daemon=True)
    state["thread"].start()
    bpy.app.timers.register(wait, first_interval=0.1)


def wait():
    """Keep the main thread free for the tool calls until the client is done."""
    state["ticks"] += 1
    if state["thread"].is_alive() and state["ticks"] < 1200:
        return 0.05
    try:
        check(not state["thread"].is_alive(), "client timed out")
        check(state["error"] is None, state["error"])
        results = state["results"]
        check("instructions" in results["init"], "no instructions")
        check("run_python" in results["tools"], results["tools"])
        shot = results["shot"]
        check(shot[0]["type"] == "image", shot)
        png = base64.b64decode(shot[0]["data"])
        check(png[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG")
        check("Window" in shot[1]["text"], shot[1]["text"])
        check(results["area_shot"][0]["type"] == "image", "area shot")
        check("SpaceView3D" not in results["view"].get("error", ""), results["view"])
        check(results["ran"]["result"] == ["FINISHED"], results["ran"])
        nodes = [n["type"] for n in results["after_undo"]["nodes"]]
        check("SNA_Node_Print" not in nodes, f"undo kept the print: {nodes}")
        check("SNA_Node_Operator" in nodes, f"undo went too far: {nodes}")
        group = results["group"]
        check(group["function"]["tree"] == "Calc", group)
        check(results["group_problems"] == {}, results["group_problems"])
        check("10.0" in results["group_ran"].get("output", ""), results["group_ran"])
        types = [n["type"] for n in results["after_ungroup"]["nodes"]]
        check(types.count("SNA_Node_Math") == 2, f"after ungroup: {types}")
        check("SNA_Node_Group" not in types, f"group node kept: {types}")
        print("GUI TEST PASSED")
    except Exception:
        traceback.print_exc()
        print("GUI TEST FAILED: " + traceback.format_exc().strip().splitlines()[-1])
    helpers.sn("src.mcp_server.server").stop()
    bpy.ops.wm.quit_blender()
    return None


def step():
    try:
        start()
    except Exception:
        traceback.print_exc()
        print("GUI TEST FAILED: " + traceback.format_exc().strip().splitlines()[-1])
        bpy.ops.wm.quit_blender()


bpy.app.timers.register(step, first_interval=1.0)
