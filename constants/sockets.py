from ..core.sockets.data.StringSocket import SN_StringSocket
from ..core.sockets.program.InterfaceSocket import SN_InterfaceSocket

INTERFACE = SN_InterfaceSocket.bl_idname
STRING = SN_StringSocket.bl_idname


SOCKET_NAMES = {
    INTERFACE: "Interface",
    STRING: "String",
}
