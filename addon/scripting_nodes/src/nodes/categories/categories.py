import inspect
from ...node_tree.node_tree import ScriptingNodeTree
import os
import bpy


class SN_MT_LayoutMenu(bpy.types.Menu):
    bl_idname = "SNA_MT_LayoutMenu"
    bl_label = "Layout"

    def draw(self, context):
        layout = self.layout
        op = layout.operator("node.add_node", text="Frame")
        op.type = "NodeFrame"
        op.use_transform = True

        op = layout.operator("node.add_node", text="Reroute")
        op.type = "NodeReroute"
        op.use_transform = True


_node_categories = {}


def category_label(dirname):
    """Display name for a category folder: `blend_data` -> `Blend Data`."""
    return dirname.replace("_", " ").title()


def menu_idname(path):
    """Unique menu idname for a category path like `data.blend_data`."""
    return "SNA_MT_category_" + path.replace(".", "_")


def get_node_categories():
    global _node_categories
    # Import auto_load lazily to avoid circular import during module initialization
    from .... import auto_load

    if _node_categories:
        return _node_categories
    else:
        node_categories = {}

        for cls in auto_load.ordered_classes:
            # issubclass picks up NodeCustomGroup subclasses too
            if isinstance(cls, type) and issubclass(cls, bpy.types.Node):
                path = os.path.dirname(inspect.getfile(cls))
                dirs = path.split(os.sep)

                if "categories" in dirs:
                    node_path = dirs[dirs.index("categories") + 1 :]
                    parent = node_categories
                    for dir in node_path:
                        if dir not in parent:
                            parent[dir] = {}
                        parent = parent[dir]
                    if "nodes" not in parent:
                        parent["nodes"] = []
                    parent["nodes"].append(cls)

        _node_categories = node_categories
        return node_categories


_registered_menus = []


@classmethod
def poll(cls, context):
    return context.space_data.tree_type == ScriptingNodeTree.bl_idname


def register_node_menus():
    categories = get_node_categories()
    for cat in sorted(categories.keys()):
        if cat == "nodes":
            continue
        register_menu(cat)
        register_category_menus(categories[cat], cat)


def register_category_menus(category, path):
    for cat in sorted(category.keys()):
        if cat == "nodes":
            continue
        register_menu(f"{path}.{cat}")
        register_category_menus(category[cat], f"{path}.{cat}")


def register_menu(path):
    menu_type = type(
        menu_idname(path),
        (bpy.types.Menu,),
        {
            "bl_space_type": "NODE_EDITOR",
            "bl_label": category_label(path.split(".")[-1]),
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
        except RuntimeError:
            pass
    _registered_menus.clear()


def draw_submenu(self, context):
    layout = self.layout

    category = get_node_categories()
    for path in self.path.split("."):
        category = category[path]

    for cat in sorted(category.keys()):
        if not cat == "nodes":
            layout.menu(menu_idname(f"{self.path}.{cat}"), text=category_label(cat))

    if "nodes" in category and len(category["nodes"]) and len(category.keys()) > 1:
        layout.separator()

    if self.path == "groups":
        draw_groups_menu(layout, context)
        return

    if "nodes" in category:
        for node in sorted(category["nodes"], key=lambda n: n.bl_label):
            # Check if node's poll method allows it in this tree
            tree = context.space_data.edit_tree
            if tree and hasattr(node, "poll") and not node.poll(tree):
                continue
            op = layout.operator("node.add_node", text=node.bl_label)
            op.type = node.bl_idname
            op.use_transform = True


def draw_groups_menu(layout, context):
    """Group Input / Output, an empty Group node and one entry per function."""
    for idname, text in (
        ("NodeGroupInput", "Group Input"),
        ("NodeGroupOutput", "Group Output"),
        ("SNA_Node_Group", "Group"),
    ):
        op = layout.operator("node.add_node", text=text)
        op.type = idname
        op.use_transform = True
    tree = context.space_data.edit_tree
    trees = [
        t
        for t in bpy.data.node_groups
        if getattr(t, "is_sn", False) and t != tree and t.is_function
    ]
    if trees:
        layout.separator()
    for function in sorted(trees, key=lambda t: t.name):
        op = layout.operator("node.add_node", text=function.name, icon="NODETREE")
        op.type = "SNA_Node_Group"
        op.use_transform = True
        setting = op.settings.add()
        setting.name = "node_tree"
        setting.value = f"bpy.data.node_groups[{function.name!r}]"


def draw_node_menu(self, context):
    if context.space_data.tree_type != ScriptingNodeTree.bl_idname:
        return
    categories = get_node_categories()
    layout = self.layout

    layout.separator()
    for cat in sorted(categories.keys()):
        if not cat == "nodes":
            layout.menu(menu_idname(cat), text=category_label(cat))

    layout.menu("SNA_MT_LayoutMenu", text="Layout")


def register():
    register_node_menus()
    bpy.types.NODE_MT_add.append(draw_node_menu)


def unregister():
    bpy.types.NODE_MT_add.remove(draw_node_menu)
    unregister_node_menus()
