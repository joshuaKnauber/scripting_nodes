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


class SN_LoadAddons(bpy.types.Operator):
    bl_idname = "scripting_nodes.load_addons"
    bl_label = "Load Addons"
    bl_description = "Loads the addons"
    bl_options = {"REGISTER","INTERNAL"}

    def execute(self, context):
        url = "https://raw.githubusercontent.com/joshuaKnauber/serpens_addon_market/main/addons.json?token=AL5DR6CIA3AQPYNR5Z2J6WS7RM46O"

        # try:
        addons = requests.get(url).json()["addons"]
        print(addons)
        shuffle(addons)
        context.scene.sn_addons.clear()
        for addon in addons:
            item = context.scene.sn_addons.add()
            item.title = addon["name"]
            item.text = addon["description"]
            item.category = addon["category"]
            item.author = addon["author"]
            item.blender_version = tuple(addon["blender_version"])
            item.addon_version = tuple(addon["addon_version"])
            item.url = addon["url"]
            item.price = addon["price"]

        # except:
        #     self.report({"ERROR"},message="Couldn't find what we were looking for. Check your connection!")
            
        return {"FINISHED"}