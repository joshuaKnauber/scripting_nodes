import bpy
from bpy_extras.io_utils import ExportHelper
import os
import shutil
from .compiler import compile_addon, remove_addon, addon_is_registered, compile_export



class SN_OT_Compile(bpy.types.Operator):
    bl_idname = "sn.compile"
    bl_label = "Compile"
    bl_description = "Compiles all graphs with changes"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    @classmethod
    def poll(cls, context):
        return context.scene.sn.addon_tree() != None

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        
        success = compile_addon(addon_tree,False)
        
        if success:
            has_fatal = False
            for error in addon_tree.sn_graphs[0].errors:
                if error.fatal:
                    has_fatal = True
            if not has_fatal:
                self.report({"INFO"},message="Successfully compiled '"+addon_tree.sn_graphs[0].name+"'!")
            else:
                self.report({"WARNING"},message="Check the N-Panel for errors in '"+addon_tree.sn_graphs[0].name+"'!")
        else:
            self.report({"ERROR"},message="Your addon could not be compiled properly! Check the console for more information.")
            print("If you don't understand where this error is coming from, you can report it in the discord server to get more information.")
            print("Please provide your compiled addon file if possible. You can get this by checking 'Show Python File' in the Serpens preferences.")
        for a in context.screen.areas: a.tag_redraw()
        return {"FINISHED"}



class SN_OT_RemoveAddon(bpy.types.Operator):
    bl_idname = "sn.remove_addon"
    bl_label = "Remove Addon"
    bl_description = "Removes this compiled addon"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    @classmethod
    def poll(cls, context):
        addon_tree = context.scene.sn.addon_tree()
        return addon_tree != None and addon_is_registered(addon_tree) and not addon_tree.sn_graphs[0].autocompile

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        
        remove_addon(addon_tree)
        addon_tree.set_changes(True)
        
        for a in context.screen.areas: a.tag_redraw()
        return {"FINISHED"}
    
    
    
class SN_OT_ExportAddon(bpy.types.Operator):
    bl_idname = "sn.save_addon"
    bl_label = "Save Addon"
    bl_description = "Saves the active addon as an installable addon"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    filepath: bpy.props.StringProperty(name="File Path", description="Filepath used for exporting the file", maxlen=1024, subtype='FILE_PATH')

    filename_ext = ".zip"
    filter_glob: bpy.props.StringProperty(default='*.zip', options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        zip_name = context.scene.sn.addon_tree().sn_graphs[0].name.lower().replace(" ","_").replace("-","_") + ".zip"
        self.filepath = os.path.join(self.filepath,zip_name)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def make_archive(self, source, destination):
        base = os.path.basename(destination)
        name = base.split('.')[0]
        format = base.split('.')[1]
        archive_from = os.path.dirname(source)
        archive_to = os.path.basename(source.strip(os.sep))
        shutil.make_archive(name, format, archive_from, archive_to)
        shutil.move('%s.%s'%(name,format), destination)

    def execute(self, context):
        if not ".zip" in self.filepath:
            self.filepath += ".zip"
        text = compile_export(context.scene.sn.addon_tree())
        if text:
            addon_tree = context.scene.sn.addon_tree()
            dir_name = addon_tree.sn_graphs[0].name.lower().replace(" ","_").replace("-","_")
            dir_path = os.path.join(os.path.dirname(self.filepath),dir_name)
            if os.path.exists(dir_path):
                self.report({"ERROR"},message="A file with this name already exists in this location!")
            else:
                os.mkdir(dir_path)
                os.mkdir(os.path.join(dir_path,"icons"))
                os.mkdir(os.path.join(dir_path,"assets"))
                
                with open(os.path.join(dir_path,"__init__.py"), "w", encoding="utf-8") as py_file:
                    py_file.write(text.as_string())
                    
                for icon in addon_tree.sn_icons:
                    if icon.image:
                        icon.image.filepath = os.path.join(dir_path, "icons", icon.name+".png")
                        icon.image.file_format = "PNG"
                        icon.image.save()

                for asset in addon_tree.sn_assets:
                    if asset.path and os.path.exists(asset.path):
                        shutil.copyfile(asset.path, os.path.join(dir_path, "assets", os.path.basename(asset.path)))
                    
                # self.make_archive(dir_path, self.filepath)
                # shutil.rmtree(dir_path)
                
                bpy.ops.sn.export_to_marketplace("INVOKE_DEFAULT")
        else:
            self.report({"ERROR"},message="Your addon could not be compiled properly! Please debug before exporting.")
        return {"FINISHED"}