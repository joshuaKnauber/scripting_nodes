import bpy
from time import time, sleep
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
    if key in ["rna_type", "bl_rna", "depsgraph", "original"]:
        return False
    return True

def is_valid_path(path, screen):
    # NOTE blender bug where it crashes when you access data from another screen
    if ".screens[" in path and not screen.name in path:
        return False
    return True


def get_data(data, path, screen, depth):
    global data_flat
    global visited_ids

    if depth > 10:
        return

    if id(data) in visited_ids and visited_ids[id(data)]["depth"] >= depth:
        return
    visited_ids[id(data)] = {
        "path": path,
        "depth": depth
    }

    keys = dir(data)
    if hasattr(data, "keyframe_insert"):
        keys += dir(bpy.types.Struct)

    for key in keys:
        if is_valid_key(key) and is_valid_path(f"{path}.{key}", screen):
            try:
                child_data = getattr(data, key)
                data_flat[f"{path}.{key}"] = { "name": key, }
                if hasattr(child_data, "bl_rna"):
                    get_data(child_data, f"{path}.{key}", screen, depth+1)

                    max_items = 20
                    if is_iterable(child_data):
                        # keyed data
                        if len(child_data.keys()) == len(child_data.values()):
                            for i, child_key in enumerate(list(child_data.keys())):
                                # if i < max_items:
                                get_data(child_data[child_key], f"{path}.{key}['{child_key}']", screen, depth+1)
                        # indexed data
                        else:
                            for i in range(min(len(child_data.values()), max_items)):
                                get_data(child_data[i], f"{path}.{key}[{i}]", screen, depth+1)
            except: pass


def is_match(path, search):
    parts = search.split(",")
    for part in parts:
        if not part.lower() in path.lower():
            return False
    return True


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
        print(f"Found {len(data_flat)} items")
        return None
    return 0.1

class SN_OT_TestGlobalSearch(bpy.types.Operator):
    bl_idname = "sn.test_global_search"
    bl_label = "Global Search (Test)"
    bl_description = "Global data search"
    bl_options = {"REGISTER"}

    def update_search(self, context):
        new_count = 0
        for key in data_flat.keys():
            if is_match(key, self.search):
                new_count += 1
        self.count = new_count

    count: bpy.props.IntProperty(name="Count")
    search: bpy.props.StringProperty(name="Search", default="", update=update_search)

    max_draw: bpy.props.IntProperty(name="Max Draw", default=100)

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "search")
        layout.prop(self, "max_draw")
        layout.label(text=f"Total Count: {len(data_flat)}")
        layout.label(text=f"Filtered Count: {self.count}")
        count = 0
        for key in data_flat.keys():
            if is_match(key, self.search) and count < self.max_draw:
                count += 1
                layout.label(text=key)

    def invoke(self, context, event):
        global thread
        global data_flat
        global visited_ids
        data_flat = {}
        visited_ids = {}
        thread = threading.Thread(target=get_data, args=(bpy.data, "bpy.data", context.screen, 1))
        thread.start()

        bpy.app.timers.register(timer, first_interval=0.1)

        return context.window_manager.invoke_popup(self, width=800)