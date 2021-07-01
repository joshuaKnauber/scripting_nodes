import bpy
from bpy_extras.io_utils import ExportHelper
import os
import shutil
from .compiler import compile_addon, remove_addon, addon_is_registered, compile_export


class SN_OT_Compile(bpy.types.Operator):
    bl_idname = "sn.compile"
    bl_label = "Compile"
    bl_description = "Compiles all graphs with changes"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        return context.scene.sn.addon_tree() != None

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()

        success = compile_addon(addon_tree, False)

        if success:
            has_fatal = False
            for error in addon_tree.sn_graphs[0].errors:
                if error.fatal:
                    has_fatal = True
            if not has_fatal:
                self.report({"INFO"}, message="Successfully compiled '" +
                            addon_tree.sn_graphs[0].name+"'!")
            else:
                self.report({"WARNING"}, message="Check the N-Panel for errors in '" +
                            addon_tree.sn_graphs[0].name+"'!")
        else:
            self.report(
                {"ERROR"}, message="Your addon could not be compiled properly! Check the console for more information.")
        for a in context.screen.areas:
            a.tag_redraw()
        return {"FINISHED"}


class SN_OT_RemoveAddon(bpy.types.Operator):
    bl_idname = "sn.remove_addon"
    bl_label = "Remove Addon"
    bl_description = "Removes this compiled addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        addon_tree = context.scene.sn.addon_tree()
        return addon_tree != None and addon_is_registered(addon_tree) and not addon_tree.sn_graphs[0].autocompile

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()

        remove_addon(addon_tree)
        addon_tree.set_changes(True)

        for a in context.screen.areas:
            a.tag_redraw()
        return {"FINISHED"}


class SN_OT_ExportAddon(bpy.types.Operator):
    bl_idname = "sn.save_addon"
    bl_label = "Save Addon"
    bl_description = "Saves the active addon as an installable addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    filepath: bpy.props.StringProperty(
        name="File Path", description="Filepath used for exporting the file", maxlen=1024, subtype='FILE_PATH')

    filename_ext = ".zip"
    filter_glob: bpy.props.StringProperty(default='*.zip', options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        graph = context.scene.sn.addon_tree().sn_graphs[0]
        zip_name = graph.name.lower().replace(" ", "_").replace("-", "_")
        zip_name += "_" + str(tuple(graph.version)).replace("(",
                                                            "").replace(")", "").replace(", ", ".") + ".zip"

        self.filepath = os.path.join(self.filepath, zip_name)

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def make_archive(self, source, destination):
        destination_folder = (".").join(destination.split('.')[:-1])
        shutil.make_archive(destination_folder, "zip", os.path.dirname(
            destination), os.path.basename(source))

    def save_image(self, img, path):
        settings = bpy.context.scene.render.image_settings
        format = settings.file_format
        mode = settings.color_mode
        depth = settings.color_depth

        settings.file_format = 'PNG'
        settings.color_mode = 'RGBA'
        settings.color_depth = '8'

        img.save_render(path)

        settings.file_format = format
        settings.color_mode = mode
        settings.color_depth = depth

    def execute(self, context):
        prefs = context.preferences.addons[__name__.partition('.')[
            0]].preferences

        if not ".zip" in self.filepath:
            self.filepath += ".zip"

        if prefs.debug_export:
            print("EXPORT PATH: "+self.filepath)

        text = compile_export(context.scene.sn.addon_tree())
        if text:

            if prefs.debug_export:
                print("LOG: Created compiled text")

            addon_tree = context.scene.sn.addon_tree()
            dir_name = addon_tree.sn_graphs[0].name.lower().replace(
                " ", "_").replace("-", "_")
            dir_path = os.path.join(os.path.dirname(self.filepath), dir_name)

            if prefs.debug_export:
                print("EXPORT DIR NAME: "+dir_name)
            if prefs.debug_export:
                print("EXPORT DIR PATH: "+dir_path)

            if os.path.exists(dir_path):
                self.report(
                    {"ERROR"}, message="A file with this name already exists in this location!")
            else:
                os.mkdir(dir_path)
                os.mkdir(os.path.join(dir_path, "icons"))
                os.mkdir(os.path.join(dir_path, "assets"))

                if prefs.debug_export:
                    print("LOG: Created folders at dir path")

                with open(os.path.join(dir_path, "__init__.py"), "w", encoding="utf-8") as py_file:
                    py_file.write(text.as_string())

                if prefs.debug_export:
                    print("LOG: Wrote __init__.py")

                for icon in addon_tree.sn_icons:
                    if icon.image:
                        self.save_image(icon.image, os.path.join(
                            dir_path, "icons", icon.name+".png"))

                if prefs.debug_export:
                    print("LOG: Saved icons")

                if context.scene.sn.easy_bpy and len(context.scene.sn.easy_bpy.lines):
                    with open(os.path.join(dir_path, "easybpy.py"), "w", encoding="utf-8") as py_file:
                        py_file.write(context.scene.sn.easy_bpy.as_string())

                if prefs.debug_export:
                    print("LOG: Saved Easy BPY")

                for asset in addon_tree.sn_assets:
                    if asset.path and os.path.exists(asset.path):
                        shutil.copyfile(asset.path, os.path.join(
                            dir_path, "assets", os.path.basename(asset.path)))

                if prefs.debug_export:
                    print("LOG: Copied assets")

                if not prefs.no_zip_export:
                    self.make_archive(dir_path, self.filepath)
                    shutil.rmtree(dir_path)

                    if prefs.debug_export:
                        print("LOG: Zipped addon")

                bpy.ops.sn.export_to_marketplace("INVOKE_DEFAULT")
        else:
            self.report(
                {"ERROR"}, message="Your addon could not be compiled properly! Please debug before exporting.")
        return {"FINISHED"}
