"""Shared by the Inline Script and Script Function nodes."""

from .....sockets.spec import Socket


def current_specs(node):
    """The sockets `node` has, to keep its links while its script is broken."""

    def spec(socket):
        result = Socket(socket.bl_idname, socket.identifier, socket.name)
        if hasattr(socket, "kind"):
            result.kind = socket.kind
        for attr in ("dimension", "use_alpha"):
            if hasattr(socket, attr):
                result.attrs[attr] = getattr(socket, attr)
        return result

    return [spec(s) for s in node.inputs], [spec(s) for s in node.outputs]
