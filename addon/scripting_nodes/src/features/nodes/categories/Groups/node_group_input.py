from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_GroupInput(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_GroupInput"
    bl_label = "Group Input"
    sn_options = {"ROOT_NODE"}

    def generate(self):
        self.code = f"""
            def {self.node_tree.module_name}():
                print("hello from group")
        """

        # # update all group nodes that use this group
        # for ntree in scripting_node_trees():
        #     for node in ntree.nodes:
        #         if (
        #             node.bl_idname == SNA_Node_Group.bl_idname
        #             and node.group_tree == self.node_tree
        #         ):
        #             node._generate()

    def on_group_socket_change(self, tree):
        self.outputs.clear()
        for socket in tree.interface.items_tree:
            if socket.in_out == "INPUT":
                self.add_output(socket.socket_type, socket.name)
        self._generate()
