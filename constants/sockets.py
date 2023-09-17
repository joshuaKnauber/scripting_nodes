from ..core.sockets.data.BooleanSocket import SN_BooleanSocket
from ..core.sockets.data.PropertySocket import SN_PropertySocket
from ..core.sockets.data.StringSocket import SN_StringSocket
from ..core.sockets.program.ExecuteSocket import SN_ExecuteSocket
from ..core.sockets.program.InterfaceSocket import SN_InterfaceSocket

EXECUTE = SN_ExecuteSocket.bl_idname
INTERFACE = SN_InterfaceSocket.bl_idname
STRING = SN_StringSocket.bl_idname
BOOLEAN = SN_BooleanSocket.bl_idname
PROPERTY = SN_PropertySocket.bl_idname


SOCKET_NAMES = {
    EXECUTE: "Execute",
    INTERFACE: "Interface",
    STRING: "String",
    BOOLEAN: "Boolean",
    PROPERTY: "Property",
}
