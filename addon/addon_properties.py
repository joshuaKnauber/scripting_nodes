import bpy
from bl_ui import space_userpref
from uuid import uuid4
from ..core.file_browser.properties.files_properties import FilesProperties


class SN_AddonProperties(bpy.types.PropertyGroup):
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
