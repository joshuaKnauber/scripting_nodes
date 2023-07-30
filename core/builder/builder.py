import bpy
from ...utils import paths
import os


def build_addon():
    module_path = os.path.join(paths.ADDON_DIRECTORY, "my_addon")
    print(module_path)
    os.mkdir(module_path)
    with open(os.path.join(module_path, "__init__.py"), "a+") as init_file:
        init_file.write("import bpy\n")
    # for ntree in bpy.data.node_groups':
    #     if ntree.bl_idname == "ScriptingNodesTree":
    #         build_node_tree(ntree)'


def build_node_tree(ntree):
    for node in ntree.nodes:
        if node.is_root:
            pass