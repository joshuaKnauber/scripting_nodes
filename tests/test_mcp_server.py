"""The MCP server must refuse requests a web page could forge."""

import json
import socket
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
