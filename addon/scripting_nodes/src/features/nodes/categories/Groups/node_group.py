from scripting_nodes.src.features.node_tree.node_tree import ScriptingNodeTree
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Group(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Group"
    bl_label = "Node Group"

    def poll_tree(self, tree):
        return tree.bl_idname == ScriptingNodeTree.bl_idname

    def update_tree(self, context):
        self._generate()

    group_tree: bpy.props.PointerProperty(
        type=bpy.types.NodeTree, poll=poll_tree, update=update_tree
    )

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row.template_ID(self, "group_tree")
        if not self.group_tree:
            op = row.operator("sna.add_group", text="New", icon="ADD")
            op.node_id = self.id

    def generate(self):
        if not self.group_tree:
            return

        if self.group_tree != self.node_tree:
            self.code_global = f"""
                from .{self.group_tree.module_name} import {self.group_tree.module_name}
            """

        self.code = f"""
            {self.group_tree.module_name}()
        """

    def on_group_socket_change(self, tree):
        if tree != self.group_tree:
            return

        self.inputs.clear()
        self.outputs.clear()
        for socket in tree.interface.items_tree:
            if socket.in_out == "INPUT":
                self.add_input(socket.socket_type, socket.name)
            elif socket.in_out == "OUTPUT":
                self.add_output(socket.socket_type, socket.name)

        self._generate()
