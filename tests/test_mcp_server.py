"""The MCP server must refuse requests a web page could forge."""

import json
import socket
import threading
import unittest
import urllib.error
import urllib.request

import helpers

INIT = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"}).encode()


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class MCPServerSecurityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = helpers.sn("src.mcp_server.server")
        cls.port = free_port()
        cls.server.start(cls.port)

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def post(self, headers):
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/", data=INIT, headers=headers
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status
        except urllib.error.HTTPError as e:
            return e.code

    def test_valid_request(self):
        self.assertEqual(self.post({"Content-Type": "application/json"}), 200)

    def test_rejects_browser_origin(self):
        status = self.post(
            {"Content-Type": "application/json", "Origin": "https://evil.example"}
        )
        self.assertEqual(status, 403)

    def test_rejects_simple_content_type(self):
        # text/plain is what a no-preflight browser fetch would send
        self.assertEqual(self.post({"Content-Type": "text/plain"}), 403)

    def test_rejects_foreign_host(self):
        status = self.post(
            {"Content-Type": "application/json", "Host": "attacker.example:80"}
        )
        self.assertEqual(status, 403)


class MCPSnippetTest(unittest.TestCase):
    """The setups the MCP Server panel copies (mcp_server/ops/server_ops.py)."""

    def setUp(self):
        self.ops = helpers.sn("src.mcp_server.ops.server_ops")
        self.prefs = helpers.sn("src.settings.preferences").get_preferences()
        self.addCleanup(setattr, self.prefs, "mcp_token", self.prefs.mcp_token)
        self.prefs.mcp_token = ""

    def test_claude_desktop_starts_mcp_remote(self):
        # claude_desktop_config.json only starts local servers: no "url"
        server = json.loads(self.ops._snippet_claude_desktop(7423))["mcpServers"][
            "scripting-nodes"
        ]
        self.assertEqual(server["command"], "npx")
        self.assertEqual(server["args"], ["-y", "mcp-remote", "http://127.0.0.1:7423/"])
        self.assertNotIn("url", server)

    def test_claude_desktop_token(self):
        self.prefs.mcp_token = "secret"
        server = json.loads(self.ops._snippet_claude_desktop(7423))["mcpServers"][
            "scripting-nodes"
        ]
        self.assertEqual(
            server["args"][-2:], ["--header", "Authorization:${SN_MCP_AUTH}"]
        )
        self.assertEqual(server["env"], {"SN_MCP_AUTH": "Bearer secret"})

    def test_json_is_http(self):
        server = json.loads(self.ops._snippet_json(7423))["mcpServers"][
            "scripting-nodes"
        ]
        self.assertEqual(server, {"type": "http", "url": "http://127.0.0.1:7423/"})


class MCPToolCallTest(unittest.TestCase):
    def test_tool_runs_on_the_main_thread(self):
        """The worker thread hands the call to the main thread's pump."""
        server = helpers.sn("src.mcp_server.server")
        bridge = helpers.sn("src.mcp_server.bridge")
        helpers.new_tree("Main")
        result = {}
        params = {"name": "get_addon", "arguments": {}}
        worker = threading.Thread(
            target=lambda: result.update(server._handle_tools_call(1, params))
        )
        worker.start()
        while worker.is_alive():
            bridge._drain()
            worker.join(0.01)
        self.assertNotIn("isError", result["result"])
        self.assertIn("Main", result["result"]["content"][0]["text"])
