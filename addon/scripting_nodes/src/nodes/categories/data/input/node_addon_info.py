import bpy

from .....core import metadata
from .....sockets.spec import String
from ....base_node import ScriptingBaseNode


class SNA_Node_AddonInfo(ScriptingBaseNode, bpy.types.Node):
    """This add-on's name, version, Python module and the folder it's
    installed in (e.g. to load files shipped with it)."""

    bl_idname = "SNA_Node_AddonInfo"
    bl_label = "Add-on Info"
    sn_outputs = [
        String("name", "Name"),
        String("version", "Version"),
        String("module", "Module"),
        String("folder", "Folder"),
    ]

    def emit(self, ctx):
        settings = bpy.context.scene.sna.addon
        ctx.output("name", repr(settings.addon_name))
        ctx.output("version", repr(metadata.version(settings.version)))
        # tree modules are <add-on>/addon/<tree>.py
        ctx.output("module", '__package__.rpartition(".")[0]')
        ctx.imports("import os")
        ctx.output("folder", "os.path.dirname(os.path.dirname(__file__))")
