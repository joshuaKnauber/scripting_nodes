from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_List(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_List"
    bl_label = "List"

    def on_create(self):
        inp = self.add_input("ScriptingDataSocket", "List Item")
        inp.is_dynamic = True

        inp = self.add_input("ScriptingDynamicAddInputSocket", "Add Input")
        inp.add_socket_type = "ScriptingDataSocket"
        inp.add_socket_name = "List Item"

        self.add_output("ScriptingListSocket", "List")

    def generate(self):
        items = []
        for i, socket in enumerate(self.inputs):
            if (
                socket.bl_idname != "ScriptingDynamicAddInputSocket"
                and socket.is_linked
            ):
                items.append(socket.eval())

        items_str = ", ".join(items)
        self.outputs[0].code = f"[{items_str}]"
