import os
import shutil

import bpy
from bpy_extras.io_utils import ExportHelper

from . import builder


class SNA_OT_ExportAddon(bpy.types.Operator, ExportHelper):
    """Export this addon as a installable zip file. Note that you do not need to have Serpens installed to use the exported addon"""

    bl_idname = "sna.export_addon"
    bl_label = "Export Addon"
    bl_options = {"REGISTER", "INTERNAL"}

    filename_ext = ".zip"

    filter_glob: bpy.props.StringProperty(
        default="*.zip",
        options={"HIDDEN"},
        maxlen=255,
    )

    def execute(self, context: bpy.types.Context):
        base_dir = os.path.dirname(self.filepath)
        if os.path.exists(base_dir):
            addon_dir = builder.get_addon_dir(base_dir, builder.module(prod_name=True))
            if os.path.exists(addon_dir):
                shutil.rmtree(addon_dir)
            builder.build_addon(
                base_dir, prod_build=True, module=builder.module(prod_name=True)
            )
            shutil.make_archive(self.filepath[:-4], "zip", addon_dir)
        return {"FINISHED"}

    def invoke(self, context, event):
        sna = context.scene.sna
        version = ".".join([str(i) for i in sna.info.version])
        self.filepath = f"{builder.module(prod_name=True)}_{version}.zip"
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
