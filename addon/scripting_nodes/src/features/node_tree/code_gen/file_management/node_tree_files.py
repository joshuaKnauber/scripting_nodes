import bpy
import os


def create_node_tree_file(path, ntree_name, code):
    with open(get_node_tree_file_path(path, ntree_name), "w") as f:
        f.write(code)
        f.truncate()


def get_node_tree_file_path(node_tree_files_path, ntree_name):
    return os.path.join(
        node_tree_files_path,
        f"{ntree_name}.py",
    )
