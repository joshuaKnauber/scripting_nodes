import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_BooleanNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_BooleanNode"
    bl_label = "Boolean"
    bl_icon = "MONKEY"
    node_color = (0,1,1)

    def inititialize(self, context):
        self.sockets.create_input(self,"STRING","String",False)
        socket = self.sockets.create_input(self,"BOOLEAN","Boolean",False)
        socket.display_boolean_text = True
        self.sockets.create_input(self,"INTEGER","Integer",False)
        self.sockets.create_input(self,"FLOAT","Float",False)
        self.sockets.create_input(self,"VECTOR","Vector",False)
        self.sockets.create_input(self,"EXECUTE","Execute",False)
        self.sockets.create_input(self,"LAYOUT","Layout",False)
        self.sockets.create_input(self,"OBJECT","Object",False)
        self.sockets.create_input(self,"DATA","Data",False)
        self.sockets.create_input(self,"SEPARATOR","",False)

    def evaluate(self, socket, input_data):
        blocks = [
                    {
                        "lines": [
                            
                        ],
                        "indented": [
                            
                        ]
                    }
                ]

        errors = []

        return {"blocks": blocks, "errors": errors}