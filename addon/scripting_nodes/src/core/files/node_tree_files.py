import os


def create_node_tree_file(path, ntree_name, code):
    """Write tree code to its file, returning True only if contents actually changed."""
    file_path = get_node_tree_file_path(path, ntree_name)
    current_code = ""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            current_code = f.read()
    if current_code == code:
        return False
    with open(file_path, "w") as f:
        f.write(code)
    return True


def get_node_tree_file_path(node_tree_files_path, ntree_name):
    return os.path.join(
        node_tree_files_path,
        f"{ntree_name}.py",
    )
