import bpy
import os


def create_node_tree_file(path, ntree_name, code):
    file_name = f"{ntree_name}.py"
    with open(os.path.join(path, file_name), "w") as f:
        f.write(code)
