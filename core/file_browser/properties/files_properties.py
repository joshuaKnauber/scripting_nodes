import bpy
import os


class FilesProperties(bpy.types.PropertyGroup):
    def update_file_name(self, context):
        if os.path.exists(self.path):
            os.rename(self.path, os.path.join(os.path.dirname(self.path), self.name))
            self["path"] = os.path.join(os.path.dirname(self.path), self.name)

    name: bpy.props.StringProperty(
        name="Name", description="Name of the file", update=update_file_name
    )

    def update_file_path(self, context):
        relpath = os.path.relpath(self.path, bpy.context.scene.sn.addon_location)
        self.indents = relpath.count(os.sep)
        self.update_child_files()

    path: bpy.props.StringProperty(
        name="Path", description="Path of the file", update=update_file_path
    )

    def update_folder_expanded(self, context):
        self.update_child_files()
        for i in range(len(context.scene.sn.file_list)):
            if context.scene.sn.file_list[i].path == self.path:
                context.scene.sn.active_file_index = i
                break

    folder_expanded: bpy.props.BoolProperty(
        name="Folder Expanded",
        description="Folder expanded",
        default=False,
        update=update_folder_expanded,
    )

    def update_child_files(self):
        for item in bpy.context.scene.sn.file_list:
            if (
                item.path.startswith(self.path)
                and item.path.count(os.sep) == self.path.count(os.sep) + 1
            ):
                item.update_file_visibility()

    def update_file_visibility(self):
        parent_path = os.path.dirname(self.path)
        paths = [item.path for item in bpy.context.scene.sn.file_list]
        if parent_path in paths:
            parent = bpy.context.scene.sn.file_list[paths.index(parent_path)]
            self.is_visible = parent.folder_expanded and parent.is_visible
        else:
            self.is_visible = True

    is_visible: bpy.props.BoolProperty(
        name="File Visible",
        description="File visible",
        default=True,
        update=lambda self, _: self.update_child_files(),
    )

    indents: bpy.props.IntProperty(name="Indents", description="Indents", default=0)
