from bpy_extras.io_utils import ImportHelper
import bpy
import os

from ...nodes.compiler import unregister_addon, compile_addon


def get_serpens_graphs():
    graphs = []
    for group in bpy.data.node_groups:
        if group.bl_idname == "ScriptingNodesTree":
            graphs.append(group)
    return graphs


def reassign_tree_indices():
    trees = []
    for ngroup in bpy.data.node_groups:
        if ngroup.bl_idname == "ScriptingNodesTree":
            trees.append(ngroup)
    trees = sorted(trees, key=lambda tree: tree.index)

    for i in range(len(trees)):
        trees[i].index = i
    return trees


class SN_OT_AddGraph(bpy.types.Operator):
    bl_idname = "sn.add_graph"
    bl_label = "Add Node Tree"
    bl_description = "Adds a node tree to the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        sn = context.scene.sn
        trees = reassign_tree_indices()

        curr_index = 0
        if (
            sn.node_tree_index < len(bpy.data.node_groups)
            and bpy.data.node_groups[sn.node_tree_index].bl_idname
            == "ScriptingNodesTree"
        ):
            curr_index = bpy.data.node_groups[sn.node_tree_index].index
            for i in range(curr_index + 1, len(trees)):
                trees[i].index += 1

        graph = bpy.data.node_groups.new("NodeTree", "ScriptingNodesTree")
        graph.index = curr_index - 1
        if sn.active_graph_category != "ALL":
            graph.category = sn.active_graph_category

        for i, group in enumerate(bpy.data.node_groups):
            if group == graph:
                sn.node_tree_index = i
        return {"FINISHED"}


class SN_OT_RemoveGraph(bpy.types.Operator):
    bl_idname = "sn.remove_graph"
    bl_label = "Remove Node Tree"
    bl_description = "Removes this node tree from the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        if context.scene.sn.node_tree_index < len(bpy.data.node_groups):
            return (
                bpy.data.node_groups[context.scene.sn.node_tree_index].bl_idname
                == "ScriptingNodesTree"
            )

    def execute(self, context):
        sn = context.scene.sn
        group = bpy.data.node_groups[sn.node_tree_index]
        curr_index = group.index
        bpy.data.node_groups.remove(group)

        trees = reassign_tree_indices()
        for tree in trees:
            if tree.index == curr_index:
                for i, ntree in enumerate(bpy.data.node_groups):
                    if ntree == tree:
                        sn.node_tree_index = i
                break
            elif tree.index == curr_index - 1:
                for i, ntree in enumerate(bpy.data.node_groups):
                    if ntree == tree:
                        sn.node_tree_index = i
                break
        else:
            sn.node_tree_index = 0

        compile_addon()
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class SN_OT_AppendGraph(bpy.types.Operator, ImportHelper):
    bl_idname = "sn.append_graph"
    bl_label = "Append Node Tree"
    bl_description = "Appends a node tree from another file to this addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    filter_glob: bpy.props.StringProperty(default="*.blend", options={"HIDDEN"})

    def execute(self, context):
        _, extension = os.path.splitext(self.filepath)
        if extension == ".blend":
            bpy.ops.sn.append_popup("INVOKE_DEFAULT", path=self.filepath)
        return {"FINISHED"}


class SN_OT_AppendPopup(bpy.types.Operator):
    bl_idname = "sn.append_popup"
    bl_label = "Append Node Tree"
    bl_description = "Appends this node tree from the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def get_graph_items(self, context):
        """Returns all node trees that can be found in the selected file"""
        items = []
        with bpy.data.libraries.load(self.path) as (data_from, _):
            for group in data_from.node_groups:
                items.append((group, group, group))
        if not items:
            items = [("NONE", "NONE", "NONE")]
        return items

    path: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    graph: bpy.props.EnumProperty(
        name="Node Tree",
        description="Node Tree to import",
        items=get_graph_items,
        options={"HIDDEN", "SKIP_SAVE"},
    )

    def execute(self, context):
        if self.graph != "NONE":
            # save previous groups
            prev_groups = bpy.data.node_groups.values()

            # append node group
            with bpy.data.libraries.load(self.path) as (_, data_to):
                data_to.node_groups = [self.graph]

            # register new graph
            new_groups = set(prev_groups) ^ set(bpy.data.node_groups.values())
            for group in new_groups:
                context.scene.sn.node_tree_index = bpy.data.node_groups.values().index(
                    group
                )
            compile_addon()

            # redraw screen
            context.area.tag_redraw()
        return {"FINISHED"}

    def draw(self, context):
        if self.graph == "NONE":
            self.layout.label(
                text="No Node Trees found in this blend file", icon="ERROR"
            )
        else:
            self.layout.prop(self, "graph", text="Node Tree")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class SN_OT_ForceCompile(bpy.types.Operator):
    bl_idname = "sn.force_compile"
    bl_label = "This might be slow for large addons!"
    bl_description = "Forces all node trees to compile"
    bl_options = {"REGISTER", "INTERNAL"}

    def fix_compile_order(self, refs):
        for node in refs.nodes:
            if node.order == 0:
                node.order = 3

    def execute(self, context):
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                for refs in ntree.node_refs:
                    refs.clear_unused_refs()
                    refs.fix_ref_names()
                    if refs.name == "SN_OnKeypressNode":
                        self.fix_compile_order(refs)
                ntree.reevaluate()
        compile_addon()
        self.report({"INFO"}, message="Compiled successfully!")
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class SN_OT_ForceUnregister(bpy.types.Operator):
    bl_idname = "sn.force_unregister"
    bl_label = "Force Unregister"
    bl_description = "Forces all node trees to unregister"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        unregister_addon()
        return {"FINISHED"}


class SN_OT_MoveNodeTree(bpy.types.Operator):
    bl_idname = "sn.move_node_tree"
    bl_label = "Move Node Tree"
    bl_description = "Moves this node tree in the list"
    bl_options = {"REGISTER", "INTERNAL"}

    move_up: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        reassign_tree_indices()

        # ntree = get_selected_graph()
        # before = get_selected_graph_offset(-1)
        # after = get_selected_graph_offset(1)

        # # move trees
        # if ntree:
        #     if self.move_up and before:
        #         temp_index = ntree.index
        #         ntree.index = before.index
        #         before.index = temp_index
        #     elif not self.move_up and after:
        #         temp_index = ntree.index
        #         ntree.index = after.index
        #         after.index = temp_index
        return {"FINISHED"}
