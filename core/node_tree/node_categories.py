from ... import auto_load
import os
import inspect
import bpy


class SN_OT_SearchNodes(bpy.types.Operator):
    bl_idname = "sn.search_nodes"
    bl_label = "Search"
    bl_description = "Search for Serpens nodes"
    bl_options = {"REGISTER", "UNDO"}
    bl_property = "node"

    def node_items(self, context):
        items = []
        for cls in auto_load.ordered_classes:
            if cls.bl_rna.base and cls.bl_rna.base.identifier == "Node":
                items.append((cls.bl_idname, cls.bl_label, cls.bl_label))
        items.append(("NodeFrame", "Frame", "Frame"))
        items.append(("NodeReroute", "Reroute", "Reroute"))
        items = sorted(items, key=lambda x: x[1])
        return items

    node: bpy.props.EnumProperty(
        name="Node", items=node_items, description="Node to add", options={"SKIP_SAVE"}
    )

    def execute(self, context):
        node = self.node
        bpy.ops.node.add_node("INVOKE_DEFAULT", type=node, use_transform=True)
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {"FINISHED"}


class SN_MT_LayoutMenu(bpy.types.Menu):
    bl_idname = "SN_MT_LayoutMenu"
    bl_label = "Layout"

    def draw(self, context):
        layout = self.layout
        op = layout.operator("node.add_node", text="Frame")
        op.type = "NodeFrame"
        op.use_transform = True

        op = layout.operator("node.add_node", text="Portal")
        op.type = "SN_PortalNode"
        op.use_transform = True

        op = layout.operator("node.add_node", text="Reroute")
        op.type = "NodeReroute"
        op.use_transform = True


class SN_MT_GroupSubMenu(bpy.types.Menu):
    bl_idname = "SN_MT_GroupSubMenu"
    bl_label = "Groups"

    def draw(self, context):
        layout = self.layout
        category = getattr(context, "group", "Other")
        categories = [group.name for group in context.scene.sn.groups]
        if category != "Other" and category.name != "Other":
            found_trees = False
            for ntree in bpy.data.node_groups:
                if ntree.bl_idname == "ScriptingNodesTree" and ntree.category == category.name:
                    row = layout.row(align=True)
                    row.operator("sn.move_group_category",
                                 icon="GREASEPENCIL", text="").ntree = ntree.name
                    found_trees = True
                    op = row.operator("sn.add_group_node", text=ntree.name)
                    op.ntree = ntree.name
            if not found_trees:
                layout.label(text="No groups")
        else:
            found_trees = False
            for ntree in bpy.data.node_groups:
                if ntree.bl_idname == "ScriptingNodesTree" and ntree.category not in categories or ntree.category == "Other":
                    found_trees = True
                    row = layout.row(align=True)
                    row.operator("sn.move_group_category",
                                 icon="GREASEPENCIL", text="").ntree = ntree.name
                    op = row.operator("sn.add_group_node", text=ntree.name)
                    op.ntree = ntree.name
            if not found_trees:
                layout.label(text="No groups")


class SN_MT_GroupMenu(bpy.types.Menu):
    bl_idname = "SN_MT_GroupMenu"
    bl_label = "Group"

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn
        layout.operator("sn.make_serpens_group", text="Make Group")
        layout.operator("sn.edit_serpens_node_group", text="Edit Group")

        layout.separator()

        op = layout.operator("node.add_node", text="Group Input")
        op.type = "SN_NodeGroupInputNode"
        op.use_transform = True

        op = layout.operator("node.add_node", text="Group Output")
        op.type = "SN_NodeGroupOutputNode"
        op.use_transform = True

        layout.separator()

        for group in sn.groups:
            row = layout.row()
            row.context_pointer_set("group", group)
            row.menu("SN_MT_GroupSubMenu", text=group.name)
        row = layout.row()
        row.menu("SN_MT_GroupSubMenu", text="Other")
        layout.operator("sn.add_group_category", icon="ADD")


_node_categories = {}


def get_node_categories():
    global _node_categories
    if _node_categories:
        return _node_categories
    else:
        node_categories = {}

        for cls in auto_load.ordered_classes:
            if cls.bl_rna.base and cls.bl_rna.base.identifier == "Node":
                path = os.path.dirname(inspect.getfile(cls))
                dirs = path.split(os.sep)

                if "nodes" in dirs:
                    node_path = dirs[dirs.index("nodes") + 1:]
                    parent = node_categories
                    for dir in node_path:
                        if not dir in parent:
                            parent[dir] = {}
                        parent = parent[dir]
                    if not "nodes" in parent:
                        parent["nodes"] = []
                    parent["nodes"].append(cls)

        _node_categories = node_categories
        return node_categories


blocklist = ["nodes", "Layout"]
_registered_menus = []


def register_node_menus():
    categories = get_node_categories()
    for cat in sorted(categories.keys()):
        if not cat in blocklist:
            register_menu(cat, cat)
            register_category_menus(categories[cat], cat)


def register_category_menus(category, path):
    for cat in sorted(category.keys()):
        if not cat in blocklist:
            register_menu(cat, f"{path}.{cat}")
            register_category_menus(category[cat], f"{path}.{cat}")


@classmethod
def poll(cls, context):
    return context.space_data.tree_type == "ScriptingNodesTree"


def register_menu(name, path):
    menu_type = type(
        "SN_MT_category_" + name.replace(" ", "_"),
        (bpy.types.Menu,),
        {
            "bl_space_type": "NODE_EDITOR",
            "bl_label": name.replace("_", " ").title(),
            "path": path,
            "poll": poll,
            "draw": draw_submenu,
        },
    )
    bpy.utils.register_class(menu_type)
    _registered_menus.append(menu_type)


def unregister_node_menus():
    for menu in _registered_menus:
        try:
            bpy.utils.unregister_class(menu)
        except:
            pass
    _registered_menus.clear()


def draw_submenu(self, context):
    layout = self.layout

    category = get_node_categories()
    for path in self.path.split("."):
        category = category[path]

    for cat in sorted(category.keys()):
        if not cat in blocklist:
            layout.menu(
                "SN_MT_category_" + cat.replace(" ", "_"),
                text=cat.replace("_", " ").title(),
            )

    if "nodes" in category and len(category["nodes"]) and len(category.keys()) > 1:
        layout.separator()

    if "nodes" in category:
        for node in sorted(category["nodes"], key=lambda n: n.bl_label):
            op = layout.operator("node.add_node", text=node.bl_label)
            op.type = node.bl_idname
            op.use_transform = True


def draw_node_menu(self, context):
    if context.space_data.tree_type != "ScriptingNodesTree":
        return
    categories = get_node_categories()
    layout = self.layout

    row = layout.row()
    row.operator_context = "INVOKE_DEFAULT"
    row.operator("sn.search_nodes", text="Search", icon="VIEWZOOM")

    layout.separator()
    for cat in sorted(categories.keys()):
        if not cat in blocklist and not cat == "Group":
            layout.menu(
                "SN_MT_category_" + cat.replace(" ", "_"),
                text=cat.replace("_", " ").title(),
            )

    layout.menu("SN_MT_LayoutMenu", text="Layout")

    layout.separator()
    layout.menu("SN_MT_GroupMenu", text="Group")
    layout.menu("SN_MT_PresetMenu", text="Presets")
