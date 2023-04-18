import bpy
import os
from .load_files import load_files


def update_file(old_path: str, new_path: str):
    """Update the data for this file after it has been changed in some way"""
    sn = bpy.context.scene.sn

    def log(message):
        print(f"SN Files: {message}")

    def add_item(path: str, index: int, visible: bool):
        item = sn.file_list.add()
        item.name = os.path.basename(path)
        item.path = path
        item.is_visible = visible
        sn.file_list.move(len(sn.file_list) - 1, index)
        sn.active_file_index = index

    # find file item
    file_item = None
    if old_path:
        for item in sn.file_list:
            if item.path == old_path:
                file_item = item
                break

    # file is not tracked yet
    if not file_item:
        dir_path = os.path.dirname(new_path)
        # file is in addon directory
        if dir_path == sn.addon_location:
            add_item(new_path, 0, True)
        else:
            parent_item_index = None
            for i, item in enumerate(sn.file_list):
                if item.path == dir_path:
                    parent_item_index = i
                    break
            # parent directory is not tracked
            if parent_item_index is None:
                load_files(sn.addon_location)
                log(
                    f"Parent directory of new file is not tracked yet: {dir_path}, triggering full reload"
                )
            # parent directory is tracked
            else:
                add_item(
                    new_path,
                    parent_item_index + 1,
                    sn.file_list[parent_item_index].folder_expanded
                    and sn.file_list[parent_item_index].is_visible,
                )

    # file is tracked
    else:
        # file path has changed
        if new_path != old_path:
            # file still exists
            if new_path:
                # more than this file has changed
                if os.path.dirname(new_path) != os.path.dirname(old_path):
                    load_files(sn.addon_location)
                    log("More than one file has changed, triggering full reload")
                # file has been renamed
                else:
                    file_item.path = new_path
                    file_item.name = os.path.basename(new_path)
            # file has been deleted
            else:
                sn.file_list.remove(file_item)
                log(f"File has been deleted: {old_path}")
