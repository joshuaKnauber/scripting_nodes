import zipfile

import bpy

from .. import compiler, scheduler
from ..build_context import building


def build_files():
    """Files of the addon as shipped: every node regenerated in build mode."""
    scheduler.flush()
    try:
        with building():
            scheduler.regenerate_all()
            return compiler.compile_addon(pretty=True)
    finally:
        # Put the dev-mode code back (nodes cache their generated code)
        scheduler.regenerate_all()


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
        self.report({"INFO"}, f"Exported to {path}")
        return {"FINISHED"}

    def invoke(self, context, event):
        self.filepath = f"{context.scene.sna.addon.module_name}.zip"
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
