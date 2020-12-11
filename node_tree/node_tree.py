import bpy


def update_create_tree():
    if bpy.context and hasattr(bpy.context,"space_data") and bpy.context.space_data and hasattr(bpy.context.space_data,"node_tree"):
        tree = bpy.context.space_data.node_tree
        if tree and tree.bl_idname == "ScriptingNodesTree" and not tree.done_setup:
            tree.setup(is_graph=True, is_main=True, addon_tree=tree)


class ScriptingNodesTree(bpy.types.NodeTree):

    bl_idname = 'ScriptingNodesTree'
    bl_label = "Visual Scripting"
    bl_icon = 'FILE_SCRIPT'
    done_setup: bpy.props.BoolProperty(default=False)


    def setup(self, is_graph, is_main, addon_tree):
        if is_graph:
            item = addon_tree.sn_graphs.add()
            addon_tree.sn_graph_index = len(addon_tree.sn_graphs)-1
        else:
            item = addon_tree.sn_functions.add()
            addon_tree.sn_function_index = len(addon_tree.sn_functions)-1

        item.addon_tree = addon_tree
        self.sn_addon_tree = addon_tree
        item.node_tree = self

        if is_graph and is_main:
            item.graph_type = "GRAPH"
            item.is_main_graph = True
            item.name = "Addon Main"

        elif is_graph and not is_main:
            item.graph_type = "GRAPH"
            item.is_main_graph = False
            item.name = "Addon Graph"

        elif not is_graph and is_main:
            item.graph_type = "FUNCTION"
            item.is_main_graph = True
            item.name = "Addon Graph"

        elif not is_graph and not is_main:
            item.graph_type = "FUNCTION"
            item.is_main_graph = False
            item.name = "Graph Function"

        bpy.context.space_data.node_tree = self
        self.done_setup = True


    def update(self):
        print("update")