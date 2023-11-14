import inspect
import os

import bpy

from .... import auto_load
from ....core.node_tree.node_tree import ScriptingNodesTree
from ....utils.is_serpens import in_sn_tree

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


blocklist = ["nodes"]  # folder names to ignore
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
def poll(cls, context: bpy.types.Context):
    return context.space_data.tree_type == ScriptingNodesTree.bl_idname


def register_menu(name: str, path: str):
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


def draw_submenu(self, context: bpy.types.Context):
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


def draw_node_menu(self, context: bpy.types.Context):
    categories = get_node_categories()
    layout = self.layout
    layout.enabled = in_sn_tree(context)
    for cat in sorted(categories.keys()):
        if not cat in blocklist and not cat == "Group":
            layout.menu(
                "SN_MT_category_" + cat.replace(" ", "_"),
                text=cat.replace("_", " ").title(),
            )

    layout.menu("SN_MT_LayoutMenu", text="Layout")

    # layout.separator()
    # layout.menu("SN_MT_GroupMenu", text="Group")
