from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_List(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_List"
    bl_label = "List"

    def on_create(self):
        self.add_input("ScriptingDataSocket", "List Item")
        self.add_input("ScriptingDataSocket", "List Item", dynamic=True)
        self.add_output("ScriptingListSocket", "List")

    def generate(self):
        sockets = [socket for socket in self.inputs[:-1] if socket.is_linked]
        items = [socket.eval() for socket in sockets]
        self.outputs[0].code = f"[{', '.join(items)}]"
