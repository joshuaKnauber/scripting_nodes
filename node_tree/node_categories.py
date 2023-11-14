from .. import auto_load
import os
import inspect
import bpy
from ..extensions import snippet_ops


def flatten_snippets(data):
    flat = []
    if type(data) == str:
        flat.append(data)
    else:
        cat = bpy.context.scene.sn.snippet_categories[data["name"]]
        for item in data["snippets"]:
            flat.extend(
                list(map(lambda x: os.path.join(cat.path, x), flatten_snippets(item)))
            )
    return flat


def get_snippet_list():
    flat_snippets = []
    for snippet in snippet_ops.loaded_snippets:
        flat_snippets.extend(flatten_snippets(snippet))
    flat_snippets = list(set(flat_snippets))

    for i, snippet in enumerate(flat_snippets):
        if os.path.basename(snippet) == snippet:
            flat_snippets[i] = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "extensions",
                "snippets",
                snippet,
            )
    return flat_snippets


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
                    node_path = dirs[dirs.index("nodes") + 1 :]
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


blocklist = ["nodes", "Snippets", "Layout", "Legacy"]
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

    layout.separator()
    for cat in sorted(categories.keys()):
        if not cat in blocklist:
            layout.menu(
                "SN_MT_category_" + cat.replace(" ", "_"),
                text=cat.replace("_", " ").title(),
            )

    layout.menu("SN_MT_LayoutMenu", text="Layout")

    layout.separator()
    layout.menu("SN_MT_PresetMenu", text="Presets")
    layout.menu("SN_MT_SnippetsMenu", text="Snippets")
