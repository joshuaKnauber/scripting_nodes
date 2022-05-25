import bpy
import time
from ...settings.data_properties import get_data_items



class SN_OT_GlobalSearch(bpy.types.Operator):
    bl_idname = "sn.global_search"
    bl_label = "Global Search"
    bl_description = "Search through all blender data"
    bl_options = {"REGISTER", "INTERNAL"}
    
    data = {"app": {}, "context": {}, "data": {}}
    
    search: bpy.props.StringProperty(name="Search Value",
                            description="The name of the property to search for",
                            default="")

    depth: bpy.props.IntProperty(name="Depth",
                            description="The amount of levels the search should go. Every level will increase the search time exponentially!",
                            default=4, min=1, soft_max=10, max=20)
    
    def get_nested_data(self, data, step):
        if step > self.depth: return
        for item in data["properties"].values():
            if item["has_properties"]:
                try:
                    item["data"]
                    item["expanded"] = True
                    item["properties"] = get_data_items(item["path"], item["data"])
                    self.get_nested_data(item, step+1)
                except:
                    item["expanded"] = False
                    item["has_properties"] = False


    def filter_data(self, data):
        delete_keys = []
        for key in data:
            self.filter_data(data[key]["properties"])
            if len(data[key]["properties"]) == 0:
                if not (self.search.lower() in key.lower() or \
                    self.search.lower() in data[key]["name"].lower()):
                    delete_keys.append(key)
                else:
                    data[key]["expanded"] = False

        for delete in delete_keys:
            del data[delete]


    def load_category(self, category):
        self.data[category] = get_data_items(f"bpy.{category}", bpy.data)
        
        for value in self.data[category].values():
            try:
                value["data"]                
                value["expanded"] = True
                value["properties"] = get_data_items(value["path"], value["data"])
                self.get_nested_data(value, 1)
            except:
                value["expanded"] = False
                value["has_properties"] = False
        
        self.filter_data(self.data[category])


    def run_search(self):
        t1 = time.time()
        self.load_category("data") # when doing context, load copied context
        t2 = time.time()
        s = round(t2-t1, 2)
        print(f"Took {s}s")

    def execute(self, context):
        self.run_search()
        context.scene.sn.overwrite_data_items(self.data)
        context.area.tag_redraw()
        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "search")
        layout.prop(self, "depth")
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)