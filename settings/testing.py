import bpy
from time import time
import threading

thread = None
data_flat_glob = {}

def is_iterable(data):
    if hasattr(data, "keys") and hasattr(data, "values"):
        return hasattr(data, "__getitem__")
    return False

def is_valid_key(key):
    if key.startswith("_"):
        return False
    if key in ["rna_type", "bl_rna", "spaces"]:
        return False
    return True

def get_data(data, path, depth):
    global data_flat_glob
    global count
    if depth > 5:
        return

    for key in dir(data):
        if is_valid_key(key):
            # print(path, key)
            try:
                child_data = getattr(data, key)
                data_flat_glob[path] = { "name": key, }
                get_data(child_data, f"{path}.{key}", depth=depth+1)
            except: pass

            max_items = 4
            if is_iterable(child_data):
                child_path = f"{path}.{key}"
                # keyed data
                if len(child_data.keys()) == len(child_data.values()):
                    max_items = 20
                    for i, key in enumerate(list(child_data.keys())):
                        if i < max_items:
                            get_data(child_data[key], f"{child_path}['{key}']", depth=depth+2)
                # indexed data
                else:
                    max_items = 20
                    for i in range(min(len(child_data.values()), max_items)):
                        get_data(child_data[i], f"{child_path}[{i}]", depth=depth+2)


def is_match(path, search):
    parts = search.split(",")
    for part in parts:
        if not part.lower() in path.lower():
            return False
    return True


def timer():
    global thread
    global data_flat_glob
    if not thread.is_alive():
        print(f"Found {len(data_flat_glob)} items")
        bpy.context.scene.sn.global_data_loading = False
        return None
    return .1

class SN_OT_TestGlobalSearch(bpy.types.Operator):
    bl_idname = "sn.test_global_search"
    bl_label = "Global Search (Test)"
    bl_description = "Global data search"
    bl_options = {"REGISTER"}

    def update_search(self, context):
        new_count = 0
        for key in data_flat_glob.keys():
            if is_match(key, self.search):
                new_count += 1
        self.count = new_count

    count: bpy.props.IntProperty(name="Count")
    search: bpy.props.StringProperty(name="Search", default="", update=update_search)

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "search")
        layout.label(text=f"Found Items Count: {self.count}")
        if self.count <= 1000:
            for key in data_flat_glob.keys():
                if is_match(key, self.search):
                    layout.label(text=key)

    def invoke(self, context, event):
        global thread
        thread = threading.Thread(target=get_data, args=(bpy.data, "bpy.data", 1))
        thread.start()

        context.scene.sn.global_data_loading = True
        bpy.app.timers.register(timer, first_interval=0.1)

        return context.window_manager.invoke_popup(self, width=500)