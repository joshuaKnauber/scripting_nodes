"""The MCP tools, by area: `blender` (Python, screenshots, undo, logs),
`addon` (settings, problems, code, export), `graph` (trees and nodes),
`definitions` (properties and functions), `texts` (scripts).

Every tool runs on Blender's main thread (server.py, bridge.py) and returns
JSON data, or an `Image`. A `ToolError` is a mistake in the call; its message
says what to do instead.
"""

from typing import NamedTuple

TOOLS: dict[str, dict] = {}


class Image(NamedTuple):
    data: bytes
    mime: str = "image/png"
    text: str = ""


class Later(NamedTuple):
    """Returned by a tool that needs Blender to draw first: the server waits
    `delay` seconds off the main thread, then runs `then()` on it."""

    then: object
    delay: float = 0.25


def tool(name, description, properties=None, required=(), writes=False):
    """Register a tool. `properties`: JSON schema of its arguments. `writes`:
    it changes the file (an undo step is pushed after it)."""

    def register(fn):
        TOOLS[name] = {
            "fn": fn,
            "description": " ".join(description.split()),
            "inputSchema": {
                "type": "object",
                "properties": properties or {},
                "required": list(required),
                "additionalProperties": False,
            },
            "writes": writes,
        }
        return fn

    return register


from . import addon, blender, definitions, graph, texts  # noqa: E402, F401
