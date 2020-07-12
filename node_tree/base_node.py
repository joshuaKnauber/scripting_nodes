import bpy
from ..handler.socket_handler import SocketHandler

class SN_ScriptingBaseNode:
    bl_width_min = 40
    bl_width_default = 160
    bl_width_max = 5000
    node_color = (0.5,0.5,0.5)

    sockets = SocketHandler()

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'SN_ScriptingNodesTree'

    def inititialize(self,context):
        pass

    def init(self,context):
        self.sockets._node = self

        self.use_custom_color = True
        self.color = self.node_color

        self.inititialize(context)

    def update_shapes(self,sockets):
        for socket in sockets:
            if socket.is_linked:
                socket.display_shape = socket.display_shape.replace("_DOT","")
            else:
                if not "_DOT" in socket.display_shape:
                    socket.display_shape += "_DOT"

    def update(self):
        self.update_shapes(self.inputs)
        self.update_shapes(self.outputs)

    def evaluate(self, socket, input_data):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines

                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines

                    ]
                }
            ],
            "errors": [
                {
                    "error": "",
                    "node": self,
                    "socket": None
                }
            ]
        }

    def get_register_block(self):
        return []

    def get_unregister_block(self):
        return []

    def required_imports(self):
        return []