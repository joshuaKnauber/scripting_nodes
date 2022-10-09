import bpy
import threading

thread = None
data_flat = {}
visited_ids = {}

def is_iterable(data):
    if hasattr(data, "keys") and hasattr(data, "values"):
        return hasattr(data, "__getitem__")
    return False

def is_valid_key(key):
    if key.startswith("_"):
        return False
    if key in ["rna_type", "bl_rna", "depsgraph", "original", "get", "find", "items", "keys", "values", "foreach_get", "foreach_set", "id_data", "tag", "pop", "keyconfigs"]:
        return False
    return True

def is_valid_path(path, screen):
    # NOTE blender bug where it crashes when you access data from another screen
    if ".screens[" in path and not screen.name in path:
        return False
    return True

def get_data_info(data, key):
    info = {
        "name": key,
        "type": type(data).__name__,
    }
    return info

def get_data(data, path, screen, depth):
    global data_flat
    global visited_ids

    if depth > 10:
        return

    data_id = data

    if data_id in visited_ids and visited_ids[data_id]["depth"] <= depth:
        return
    visited_ids[data_id] = {
        "path": path,
        "depth": depth
    }

    keys = dir(data)
    if hasattr(data, "keyframe_insert"):
        keys += dir(bpy.types.Struct)

    for key in keys:
        child_path = f"{path}.{key}"
        if is_valid_key(key) and is_valid_path(child_path, screen):
            try:
                child_data = getattr(data, key)
                data_flat[child_path] = get_data_info(child_data, key)
                if hasattr(child_data, "bl_rna"):
                    get_data(child_data, child_path, screen, depth+1)

                    max_items = 20
                    if is_iterable(child_data):
                        # keyed data
                        if len(child_data.keys()) == len(child_data.values()):
                            for i, child_key in enumerate(list(child_data.keys())):
                                get_data(child_data[child_key], f"{child_path}['{child_key}']", screen, depth+1)
                        # indexed data
                        else:
                            for i in range(min(len(child_data.values()), max_items)):
                                get_data(child_data[i], f"{child_path}[{i}]", screen, depth+1)
            except: pass


def timer():
    global thread
    global data_flat
    if not thread.is_alive():
        keys = list(data_flat.keys())
        keys.sort(key=len)
        new_data = {}
        for key in keys:
            new_data[key] = data_flat[key]
        data_flat = new_data
        bpy.context.scene.sn.discover_search = bpy.context.scene.sn.discover_search
        return None
    return 0.1


def start_get_data(context):
    global thread
    global data_flat
    global visited_ids

    data_flat = {}
    visited_ids = {}

    thread = threading.Thread(target=get_data, args=(bpy.data, "bpy.data", context.screen, 1))
    thread.start()

    bpy.app.timers.register(timer, first_interval=0.1)