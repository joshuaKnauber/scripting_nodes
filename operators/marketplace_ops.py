import bpy
import requests
from random import shuffle


class SN_LoadMarketplace(bpy.types.Operator):
    bl_idname = "scripting_nodes.load_marketplace"
    bl_label = "Load Marketplace"
    bl_description = "Loads the marketplace"
    bl_options = {"REGISTER","INTERNAL"}

    def execute(self, context):
        url = "https://raw.githubusercontent.com/joshuaKnauber/visual_scripting_addon_docs/packages/packages.json"

        try:
            packages = requests.get(url).json()["packages"]
            shuffle(packages)
            context.scene.sn_marketplace.clear()
            for package in packages:
                item = context.scene.sn_marketplace.add()
                item.title = package["title"]
                item.text = (";;;").join(package["text"])
                item.price = package["price"]
                item.url = package["url"]

        except:
            self.report({"ERROR"},message="Couldn't find what we were looking for. Check your connection!")
            
        return {"FINISHED"}