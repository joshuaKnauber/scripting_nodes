from ..core.sockets.data.DataSocket import SNA_DataSocket
from ..core.sockets.data.BooleanSocket import SNA_BooleanSocket
from ..core.sockets.data.FloatSocket import SNA_FloatSocket
from ..core.sockets.data.IntSocket import SNA_IntSocket
from ..core.sockets.data.IconSocket import SNA_IconSocket
from ..core.sockets.data.FloatVectorSocket import SNA_FloatVectorSocket
from ..core.sockets.data.PropertySocket import SNA_PropertySocket
from ..core.sockets.data.StringSocket import SNA_StringSocket
from ..core.sockets.data.EnumSocket import SNA_EnumSocket
from ..core.sockets.data.ListSocket import SNA_ListSocket
from ..core.sockets.data.DictSocket import SNA_DictSocket
from ..core.sockets.program.ExecuteSocket import SNA_ExecuteSocket
from ..core.sockets.program.InterfaceSocket import SNA_InterfaceSocket
from ..core.sockets.program.ProgramSocket import SNA_ProgramSocket

EXECUTE = SNA_ExecuteSocket.bl_idname
INTERFACE = SNA_InterfaceSocket.bl_idname
PROGRAM = SNA_ProgramSocket.bl_idname
DATA = SNA_DataSocket.bl_idname
STRING = SNA_StringSocket.bl_idname
ENUM = SNA_EnumSocket.bl_idname
BOOLEAN = SNA_BooleanSocket.bl_idname
FLOAT = SNA_FloatSocket.bl_idname
INT = SNA_IntSocket.bl_idname
ICON = SNA_IconSocket.bl_idname
FLOAT_VECTOR = SNA_FloatVectorSocket.bl_idname
LIST = SNA_ListSocket.bl_idname
DICT = SNA_DictSocket.bl_idname
PROPERTY = SNA_PropertySocket.bl_idname


SOCKET_NAMES = {
    EXECUTE: "Execute",
    INTERFACE: "Interface",
    PROGRAM: "Program",
    DATA: "Data",
    STRING: "String",
    ENUM: "Enum",
    BOOLEAN: "Boolean",
    FLOAT: "Float",
    INT: "Integer",
    ICON: "Icon",
    FLOAT_VECTOR: "Float Vector",
    LIST: "List",
    DICT: "Dictionary",
    PROPERTY: "Property",
}


VARIABLE_SOCKETS = {
    "DATA": DATA,
    "BOOLEAN": BOOLEAN,
    "STRING": STRING,
    "INT": INT,
    "FLOAT": FLOAT,
    "LIST": LIST,
    "DICT": DICT,
    "POINTER": PROPERTY,  #
    "COLLECTION": PROPERTY,  #
}
