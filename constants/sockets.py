from ..core.sockets.data.BooleanSocket import SNA_BooleanSocket
from ..core.sockets.data.FloatSocket import SNA_FloatSocket
from ..core.sockets.data.FloatVectorSocket import SNA_FloatVectorSocket
from ..core.sockets.data.PropertySocket import SNA_PropertySocket
from ..core.sockets.data.StringSocket import SNA_StringSocket
from ..core.sockets.program.ExecuteSocket import SNA_ExecuteSocket
from ..core.sockets.program.InterfaceSocket import SNA_InterfaceSocket

EXECUTE = SNA_ExecuteSocket.bl_idname
INTERFACE = SNA_InterfaceSocket.bl_idname
STRING = SNA_StringSocket.bl_idname
BOOLEAN = SNA_BooleanSocket.bl_idname
FLOAT = SNA_FloatSocket.bl_idname
FLOAT_VECTOR = SNA_FloatVectorSocket.bl_idname
PROPERTY = SNA_PropertySocket.bl_idname


SOCKET_NAMES = {
    EXECUTE: "Execute",
    INTERFACE: "Interface",
    STRING: "String",
    BOOLEAN: "Boolean",
    FLOAT: "Float",
    FLOAT_VECTOR: "Float Vector",
    PROPERTY: "Property",
}
