"""The export of the example add-on (Object Toolkit,
tests/visual/scenarios/_toolkit_demo.py) against its snapshot in
tests/snapshots/object_toolkit/.

A change of the generated code shows up as a diff here. When it's intended:

    SN_UPDATE_SNAPSHOTS=1 python scripts/test.py -k example_addon
"""

import difflib
import os
import shutil
import sys
import unittest

import helpers

TESTS = os.path.dirname(os.path.abspath(__file__))
SNAPSHOT = os.path.join(TESTS, "snapshots", "object_toolkit")
sys.path.insert(0, os.path.join(TESTS, "visual", "scenarios"))


def read_snapshot():
    files = {}
    for root, _, names in os.walk(SNAPSHOT):
        for name in names:
            path = os.path.join(root, name)
            rel = os.path.relpath(path, SNAPSHOT).replace(os.sep, "/")
            with open(path, "rb") as f:
                files[rel] = f.read()
    return files


def write_snapshot(files):
    shutil.rmtree(SNAPSHOT, ignore_errors=True)
    for rel, data in files.items():
        path = os.path.join(SNAPSHOT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)


def mcp_call(tool, /, **arguments):
    """A tool call the way the MCP server runs it."""
    server = helpers.sn("src.mcp_server.server")
    spec = server.TOOLS[tool]
    result = server._run_tool(spec["fn"], arguments, tool, spec["writes"])
    while isinstance(result, server.Later):
        result = result.then()
    return result


class ExampleAddonTest(unittest.TestCase):
    def test_export_matches_snapshot(self):
        import _toolkit_demo

        helpers.reset_file()
        _toolkit_demo.build()
        self.assertExportMatches()

    def test_built_through_mcp_matches_snapshot(self):
        """An agent can build the whole add-on with the MCP tools."""
        import mcp_toolkit

        helpers.reset_file()
        mcp_toolkit.build(mcp_call)
        self.assertEqual(mcp_call("get_problems"), {})
        self.assertExportMatches()

    def assertExportMatches(self):
        errors = helpers.sn("src.core.errors")
        failed = [
            f"{tree.name} / {node.name}: {errors.node_message(node.id)}"
            for tree in __import__("bpy").data.node_groups
            for node in tree.nodes
            if getattr(node, "id", "") and errors.node_message(node.id)
        ]
        self.assertEqual(failed, [])
        files = helpers.sn("src.core.ops.export").build_files()
        files = {
            rel: data if isinstance(data, bytes) else data.encode()
            for rel, data in files.items()
        }
        for rel, data in files.items():
            if rel.endswith(".py"):
                compile(data, rel, "exec")
        if os.environ.get("SN_UPDATE_SNAPSHOTS"):
            write_snapshot(files)
            return
        snapshot = read_snapshot()
        self.assertEqual(sorted(files), sorted(snapshot), "files differ")
        diffs = []
        for rel in sorted(files):
            if files[rel] != snapshot[rel]:
                diffs += difflib.unified_diff(
                    snapshot[rel].decode().splitlines(),
                    files[rel].decode().splitlines(),
                    f"snapshot/{rel}",
                    f"export/{rel}",
                    lineterm="",
                )
        if diffs:
            self.fail(
                "The export differs from tests/snapshots/object_toolkit "
                "(SN_UPDATE_SNAPSHOTS=1 updates it):\n" + "\n".join(diffs[:200])
            )
