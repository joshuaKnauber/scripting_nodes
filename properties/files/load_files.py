import bpy
import os


LOAD_EXTENSIONS = ["py", "txt", "json", "blend", "jpg", "png"]


def load_files(path: str):
    """Loads all the files for the given path into the file_list property"""
    sn = bpy.context.scene.sn
    if not sn.use_files:
        return

    active_path = sn.active_file.path if sn.active_file else ""

    # get expanded paths
    expanded_paths = []
    for item in sn.file_list:
        if item.folder_expanded:
            expanded_paths.append(item.path)

    # get all paths
    paths = []
    for root, dirs, files in os.walk(path):
        paths += [os.path.join(root, dir) for dir in dirs]
        paths += [
            os.path.join(root, file)
            for file in files
            if file.split(".")[-1] in LOAD_EXTENSIONS
        ]

    # clear file_list
    sn.file_list.clear()

    # sort paths to put parent paths before child paths and dirs before files
    sorted_paths = []
    for path in sorted(paths, key=lambda path: path.count(os.sep)):
        parent_path = os.path.dirname(path)
        if parent_path in paths:
            index = sorted_paths.index(parent_path)
            if os.path.isfile(path):
                while index < len(sorted_paths) - 1:
                    if sorted_paths[index + 1].count(os.sep) == path.count(
                        os.sep
                    ) and os.path.isdir(sorted_paths[index + 1]):
                        index += 1
                    else:
                        break
            sorted_paths.insert(index + 1, path)
        else:
            sorted_paths.append(path)

    # add paths to file_list
    for path in sorted_paths:
        item = sn.file_list.add()
        item.name = os.path.basename(path)
        item.path = path

    # load expanded and active
    active_index = 0
    for i, item in enumerate(sn.file_list):
        item.folder_expanded = item.path in expanded_paths
        if item.path == active_path:
            active_index = i
    sn.active_file_index = active_index
