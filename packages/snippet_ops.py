import bpy
from bpy_extras.io_utils import ImportHelper
import os
import shutil
import json
import zipfile


class SN_SnippetCategory(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    path: bpy.props.StringProperty()


loaded_snippets = [] # temp var for the loaded snippets

def load_snippets():
    global loaded_snippets
    installed_path = os.path.join(os.path.dirname(__file__),"installed.json")
    with open(installed_path, "r") as installed:
        data = json.loads(installed.read())
        loaded_snippets = data["snippets"]
        
        bpy.context.scene.sn.snippet_categories.clear()
        for snippet in data["snippets"]:
            if not type(snippet) == str:
                item = bpy.context.scene.sn.snippet_categories.add()
                item.name = snippet["name"]
                item.path = os.path.join(os.path.dirname(installed_path), "snippets", snippet["name"])



class SN_OT_InstallSnippet(bpy.types.Operator, ImportHelper):
    bl_idname = "sn.install_snippet"
    bl_label = "Install Snippet"
    bl_description = "Install a single or a zip file of snippets"
    bl_options = {"REGISTER", "INTERNAL"}
    
    filter_glob: bpy.props.StringProperty( default='*.json;*.zip', options={'HIDDEN'} )

    def execute(self, context):
        _, extension = os.path.splitext(self.filepath)
        with open(os.path.join(os.path.dirname(__file__), "installed.json"), "r+") as data_file:
            data = json.loads(data_file.read())
            name = os.path.basename(self.filepath)
            if not name in data["snippets"]:
                if extension == ".json":
                    data["snippets"].append(name)
                    shutil.copyfile(self.filepath, os.path.join(os.path.dirname(__file__), "snippets", name))
                if extension == ".zip":
                    name = name.split(".")[0]
                    path = os.path.join(os.path.dirname(__file__), "snippets", name)
                    with zipfile.ZipFile(self.filepath, 'r') as zip_ref:
                        zip_ref.extractall(path)
                    data["snippets"].append({
                            "name": name,
                            "snippets": os.listdir(path)
                        })
            data_file.seek(0)
            data_file.write(json.dumps(data, indent=4))
            data_file.truncate()
            load_snippets()
            self.report({"INFO"}, message="Snippet installed!")
        return {"FINISHED"}
    
    
    
class SN_OT_UninstallSnippet(bpy.types.Operator):
    bl_idname = "sn.uninstall_snippet"
    bl_label = "Uninstall Snippet"
    bl_description = "Uninstalls this snippet"
    bl_options = {"REGISTER", "INTERNAL"}
    
    index: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        path = os.path.join(os.path.dirname(__file__))
        with open(os.path.join(path, "installed.json"), "r+") as data_file:
            data = json.loads(data_file.read())
            snippet = data["snippets"].pop(self.index)
            data_file.seek(0)
            data_file.write(json.dumps(data, indent=4))
            data_file.truncate()
            if type(snippet) == str:
                os.remove(os.path.join(path, "snippets", snippet))
            else:
                shutil.rmtree(os.path.join(path, "snippets", snippet["name"]))
            load_snippets()
            self.report({"INFO"}, message="Snippet uninstalled!")
        return {"FINISHED"}
    
    
    
class SN_OT_AddSnippet(bpy.types.Operator):
    bl_idname = "sn.add_snippet"
    bl_label = "Add Snippet"
    bl_description = "Adds this snippets node"
    bl_options = {"REGISTER", "INTERNAL"}
    
    path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        bpy.ops.node.add_node("INVOKE_DEFAULT", type="SN_SnippetNode", use_transform=True)
        context.space_data.node_tree.nodes.active.path = self.path
        return {"FINISHED"}



class SN_OT_ExportSnippet(bpy.types.Operator):
    bl_idname = "sn.export_snippet"
    bl_label = "Export Snippet"
    bl_description = "Export this node as a snippet"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        
        return {"FINISHED"}
