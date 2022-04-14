import bpy
import requests
from random import shuffle



class SN_Addon(bpy.types.PropertyGroup):
    
    name: bpy.props.StringProperty()
    description: bpy.props.StringProperty()
    price: bpy.props.StringProperty()
    category: bpy.props.StringProperty()
    author: bpy.props.StringProperty()
    blender_version: bpy.props.IntVectorProperty(size=3)
    addon_version: bpy.props.IntVectorProperty(size=3)
    is_external: bpy.props.BoolProperty()
    has_blend: bpy.props.BoolProperty()
    addon_url: bpy.props.StringProperty()
    blend_url: bpy.props.StringProperty()
    serpens_version: bpy.props.IntProperty()
    
class SN_Package(bpy.types.PropertyGroup):
    
    name: bpy.props.StringProperty()
    description: bpy.props.StringProperty()
    price: bpy.props.StringProperty()
    author: bpy.props.StringProperty()
    url: bpy.props.StringProperty()
    serpens_version: bpy.props.IntProperty()
    
class SN_Snippet(bpy.types.PropertyGroup):
    
    name: bpy.props.StringProperty()
    description: bpy.props.StringProperty()
    price: bpy.props.StringProperty()
    author: bpy.props.StringProperty()
    url: bpy.props.StringProperty()
    blend_url: bpy.props.StringProperty()
    serpens_version: bpy.props.IntProperty()



class SN_OT_LoadAddons(bpy.types.Operator):
    bl_idname = "sn.load_addons"
    bl_label = "Load Addons"
    bl_description = "Loads the addons from the marketplace"
    bl_options = {"REGISTER","INTERNAL","UNDO"}

    def execute(self, context):
        url = "https://raw.githubusercontent.com/joshuaKnauber/serpens_addon_market/main/addons.json"

        try:
            content = requests.get(url).json()
            addons = content["addons"]
            shuffle(addons)
            
            context.scene.sn.addons.clear()
            for addon in addons:
                item = context.scene.sn.addons.add()
                item.name = addon["name"]
                if addon["price"]: item.price = addon["price"]
                item.description = addon["description"]
                item.category = addon["category"]
                item.author = addon["author"]
                item.blender_version = addon["blender_version"]
                item.addon_version = addon["addon_version"]
                item.is_external = addon["external"]
                item.has_blend = addon["blend"]
                item.addon_url = addon["url"]
                item.blend_url = addon["blend_url"]
                item.serpens_version = 2 if not "serpens_version" in addon else 3
        except:
            self.report({"ERROR"}, message="Couldn't load addons!")
        return {"FINISHED"}



class SN_OT_LoadPackages(bpy.types.Operator):
    bl_idname = "sn.load_packages"
    bl_label = "Load Packages"
    bl_description = "Loads the packages from the marketplace"
    bl_options = {"REGISTER","INTERNAL","UNDO"}

    def execute(self, context):
        url = "https://raw.githubusercontent.com/joshuaKnauber/serpens_addon_market/main/packages.json"

        try:
            content = requests.get(url).json()
            packages = content["packages"]
            shuffle(packages)
           
            context.scene.sn.packages.clear()
            for package in packages:
                item = context.scene.sn.packages.add()
                item.name = package["title"]
                item.description = package["description"]
                item.price = package["price"]
                item.url = package["url"]
                item.author = package["author"]
                item.serpens_version = 2 if not "serpens_version" in package else 3

        except:
            print("Couldn't load packages!")
        return {"FINISHED"}



class SN_OT_LoadSnippets(bpy.types.Operator):
    bl_idname = "sn.load_snippets"
    bl_label = "Load Snippets"
    bl_description = "Loads the snippets from the marketplace"
    bl_options = {"REGISTER","INTERNAL","UNDO"}

    def execute(self, context):
        url = "https://raw.githubusercontent.com/joshuaKnauber/serpens_addon_market/main/snippets.json"

        try:
            content = requests.get(url).json()
            snippets = content["snippets"]
            shuffle(snippets)

            context.scene.sn.snippets.clear()
            for snippet in snippets:
                item = context.scene.sn.snippets.add()
                item.name = snippet["title"]
                item.description = snippet["description"]
                item.price = snippet["price"]
                item.url = snippet["url"]
                item.blend_url = snippet["blend_url"]
                item.author = snippet["author"]
                item.serpens_version = 2 if not "serpens_version" in snippet else snippet["serpens_version"]

        except:
            print("Couldn't load snippets!")
        return {"FINISHED"}
