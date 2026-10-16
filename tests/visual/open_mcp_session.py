"""Opens GUI Blender with this checkout's add-on and the MCP server running
on its port (default 7423), an empty file to build in. Run by
scripts/open_example.py:

    python scripts/open_example.py tests/visual/open_mcp_session.py
"""

import os
import sys
import traceback

import bpy

TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TESTS_DIR)

import helpers  # noqa: E402

OUTPUT = sys.argv[sys.argv.index("--") + 1]


def start():
    try:
        helpers.enable_addon()
        prefs = helpers.sn("src.settings.preferences").get_preferences()
        server = helpers.sn("src.mcp_server.server")
        if not server.is_running():
            server.start(prefs.mcp_port)
        window = bpy.context.window_manager.windows[0]
        area = max(window.screen.areas, key=lambda a: a.width * a.height)
        region = next(r for r in area.regions if r.type == "WINDOW")
        with bpy.context.temp_override(window=window, area=area, region=region):
            bpy.ops.screen.area_split(direction="VERTICAL", factor=0.6)
        views = [a for a in window.screen.areas if a.type == "VIEW_3D"]
        left = min(views, key=lambda a: a.x)
        left.type = "NODE_EDITOR"
        left.spaces.active.tree_type = "ScriptingNodeTree"
        for area in window.screen.areas:
            if area.type in ("NODE_EDITOR", "VIEW_3D"):
                area.spaces.active.show_region_ui = True
        bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
        print("EXAMPLE READY", OUTPUT, flush=True)
    except Exception:
        traceback.print_exc()
        print("EXAMPLE FAILED", flush=True)


bpy.app.timers.register(start, first_interval=0.5)
