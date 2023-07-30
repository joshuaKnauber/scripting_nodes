import bpy
from bl_ui import space_userpref
from ..core.file_browser.properties.files_properties import FilesProperties
from .addon_info import SN_AddonInfoProperties
from .node_references import SN_NodeReference
from .group_properties import SN_GroupProperties


class SN_AddonProperties(bpy.types.PropertyGroup):
    dev_logs: bpy.props.BoolProperty(
        default=False, name="Developer Logs", description="Show developer logs in the console")

    last_generate_time: bpy.props.FloatProperty(default=0)

    # split this up in sub property groups that all live in here
    use_addon: bpy.props.BoolProperty(
        default=False,
        name="Use Addon",
        description="Generates files for the node trees in this addon that can be installed as an addon",
    )

    use_files: bpy.props.BoolProperty(
        default=False,
        name="Use Files",
        description="Lets you edit the file structure of the addon and add custom files",
    )

    use_external: bpy.props.BoolProperty(
        default=False,
        name="Extend External Addon",
        description="Lets you select an external addon to edit and add files to",
    )

    file_list: bpy.props.CollectionProperty(type=FilesProperties)

    active_file_index: bpy.props.IntProperty()

    @property
    def active_file(self):
        return (
            self.file_list[self.active_file_index]
            if len(self.file_list) > self.active_file_index
            else None
        )

    addon_location: bpy.props.StringProperty(
        name="Addon Location",
        description="Location of the addon files",
        subtype="DIR_PATH",
    )

    info: bpy.props.PointerProperty(type=SN_AddonInfoProperties)

    groups: bpy.props.CollectionProperty(type=SN_GroupProperties)

    nodes: bpy.props.CollectionProperty(type=SN_NodeReference)

    def add_node(self, node):
        item = self.nodes.add()
        item.name = node.name
        item.id = node.id

    def remove_node(self, id):
        for i, node in enumerate(self.nodes):
            if node.id == id:
                self.nodes.remove(i)
                return

    debug_code: bpy.props.BoolProperty(
        default=False,
        name="Debug Code",
        description="Show the generated code on the nodes",
    )
