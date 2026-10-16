import zipfile

import bpy

from .. import compiler, export_check, scheduler


def build_files():
    """Files of the addon as shipped (export build, formatted)."""
    scheduler.flush()  # sockets / references up to date
    return compiler.compile_addon(dev=False, pretty=True)


def write_zip(path, files):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel, source in sorted(files.items()):
            zf.writestr(rel, source)


class SNA_OT_ExportAddon(bpy.types.Operator):
    bl_idname = "sna.export_addon"
    bl_label = "Export Addon"
    bl_description = "Export the current file as an installable addon (.zip)"
    bl_options = {"REGISTER"}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.zip", options={"HIDDEN"})

    def execute(self, context):
        path = (
            self.filepath if self.filepath.endswith(".zip") else self.filepath + ".zip"
        )
        files = build_files()
        if not files:
            self.report({"ERROR"}, "Nothing to export - add a node tree first")
            return {"CANCELLED"}
        try:
            write_zip(path, files)
        except OSError as exc:
            self.report({"ERROR"}, f"Export failed: {exc}")
            return {"CANCELLED"}
        issues = export_check.run()
        if issues:
            self.report(
                {"WARNING"},
                f"Exported to {path}. {len(issues)} things to fix for the "
                "extensions platform, see Addon > Extensions Platform",
            )
        else:
            self.report({"INFO"}, f"Exported to {path}")
        return {"FINISHED"}

    def invoke(self, context, event):
        self.filepath = f"{context.scene.sna.addon.module_name}.zip"
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SNA_OT_CheckExport(bpy.types.Operator):
    bl_idname = "sna.check_export"
    bl_label = "Check"
    bl_description = (
        "Check the add-on against the moderation guidelines of the extensions platform"
    )
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        scheduler.flush()
        issues = export_check.run()
        if issues:
            self.report({"WARNING"}, f"{len(issues)} things to fix")
        else:
            self.report({"INFO"}, "Nothing to fix")
        return {"FINISHED"}
