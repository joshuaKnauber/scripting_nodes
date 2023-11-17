from ..core.sockets.data.BooleanSocket import SNA_BooleanSocket
from ..core.sockets.data.PropertySocket import SNA_PropertySocket
from ..core.sockets.data.StringSocket import SNA_StringSocket
from ..core.sockets.program.ExecuteSocket import SNA_ExecuteSocket
from ..core.sockets.program.InterfaceSocket import SNA_InterfaceSocket

EXECUTE = SNA_ExecuteSocket.bl_idname
INTERFACE = SNA_InterfaceSocket.bl_idname
STRING = SNA_StringSocket.bl_idname
BOOLEAN = SNA_BooleanSocket.bl_idname
PROPERTY = SNA_PropertySocket.bl_idname


SOCKET_NAMES = {
    EXECUTE: "Execute",
    INTERFACE: "Interface",
    STRING: "String",
    BOOLEAN: "Boolean",
    PROPERTY: "Property",
}
