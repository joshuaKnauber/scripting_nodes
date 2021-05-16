import bpy
import os
import json
import zipfile
import shutil
from bpy_extras.io_utils import ImportHelper


class SN_OT_InstallSnippets(bpy.types.Operator, ImportHelper):
    bl_idname = "sn.install_snippets"
    bl_label = "Install Snippets"
    bl_description = "Let's you install snippets from a json or zip file"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    filter_glob: bpy.props.StringProperty( default='*.zip;*.json', options={'HIDDEN'} )

    files: bpy.props.CollectionProperty(name='File paths', type=bpy.types.OperatorFileListElement)
    
    def extract_zip(self):
        snippet_directory = os.path.join(os.path.dirname(__file__), "files")
        names = []
        with zipfile.ZipFile(self.filepath, 'r') as zip_ref:
            zip_ref.extractall(snippet_directory)
            names = zip_ref.namelist()
        return names
    
    def write_to_installed(self, key, write_data):
        installed_path = os.path.join(os.path.dirname(__file__),"installed.json")
        with open(installed_path,"r+") as installed:
            data = json.loads(installed.read())
            data[key].append(write_data)
            installed.seek(0)
            installed.write(json.dumps(data,indent=4))
            installed.truncate()

    def snippet_data(self, filepath):
        snippet_data = None
        with open(filepath, "r") as snippet:
            snippet_data = json.loads(snippet.read())
        return {"name": snippet_data["name"], "filename": os.path.basename(filepath)}

    def execute(self, context):
        install_to = os.path.join(os.path.dirname(__file__), "files")
        for filepath in self.files:
            filepath = os.path.join(os.path.dirname(self.filepath), filepath.name)
            filename, extension = os.path.splitext(filepath)

            if extension == ".zip":
                extracted_files = self.extract_zip()
                category = {"name":os.path.basename(filename), "snippets":[]}
                for snippet in extracted_files:
                    category["snippets"].append(self.snippet_data(os.path.join(install_to, snippet)))
                self.write_to_installed("categories", category)
            
            elif extension == ".json":
                new_path = os.path.join(install_to, os.path.basename(filepath))
                shutil.copy(filepath, new_path)
                self.write_to_installed("snippets",self.snippet_data(new_path))
        return {"FINISHED"}



class SN_OT_UninstallSnippet(bpy.types.Operator):
    bl_idname = "sn.uninstall_snippet"
    bl_label = "Uninstall Snippet"
    bl_description = "Uninstalls this snippet"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    has_category: bpy.props.BoolProperty()
    categoryIndex: bpy.props.IntProperty()
    snippetIndex: bpy.props.IntProperty()

    def remove_from_category(self):
        installed_path = os.path.join(os.path.dirname(__file__),"installed.json")
        with open(installed_path,"r+") as installed:
            data = json.loads(installed.read())
            removed_snippet = data["categories"][self.categoryIndex]["snippets"].pop(self.snippetIndex)
            installed.seek(0)
            installed.write(json.dumps(data,indent=4))
            installed.truncate()
        return removed_snippet

    def remove_from_snippets(self):
        installed_path = os.path.join(os.path.dirname(__file__),"installed.json")
        with open(installed_path,"r+") as installed:
            data = json.loads(installed.read())
            removed_snippet = data["snippets"].pop(self.snippetIndex)
            installed.seek(0)
            installed.write(json.dumps(data,indent=4))
            installed.truncate()
        return removed_snippet
    
    def execute(self, context):
        if self.has_category:
            removed_snippet = self.remove_from_category()
        else:
            removed_snippet = self.remove_from_snippets()

        remove_from = os.path.join(os.path.dirname(__file__), "files")
        path = os.path.join(remove_from, removed_snippet["filename"])
        if os.path.exists(path):
            os.remove(path)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)



class SN_OT_UninstallSnippetCategory(bpy.types.Operator):
    bl_idname = "sn.uninstall_snippet_category"
    bl_label = "Uninstall Snippet Category"
    bl_description = "Uninstalls this snippet category"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    categoryIndex: bpy.props.IntProperty()
    
    def execute(self, context):
        installed_path = os.path.join(os.path.dirname(__file__),"installed.json")

        with open(installed_path, "r") as data:
            data = json.loads(data.read())

        for i in range(len(data["categories"][self.categoryIndex]["snippets"])-1, -1, -1):
            bpy.ops.sn.uninstall_snippet(has_category=True, categoryIndex=self.categoryIndex, snippetIndex=i)

        with open(installed_path, "r+") as installed:
            data = json.loads(installed.read())
            data["categories"].pop(self.categoryIndex)
            installed.seek(0)
            installed.write(json.dumps(data,indent=4))
            installed.truncate()
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)