"""Files and folders. Paths starting with // are relative to the .blend
file. Nodes that touch files ask for the `files` permission (manifest)."""

import bpy

from ....sockets.spec import Boolean, Flow, List, String
from ...base_node import ScriptingBaseNode

FILES = ("files",)


class SNA_Node_ReadTextFile(ScriptingBaseNode, bpy.types.Node):
    """The text of a file ("" if it doesn't exist) and its lines."""

    bl_idname = "SNA_Node_ReadTextFile"
    bl_label = "Read Text File"
    sn_permissions = FILES
    sn_inputs = [String("path", "Path")]
    sn_outputs = [String("text", "Text"), List("lines", "Lines")]

    def emit(self, ctx):
        text = f"{ctx.helper('sn_read_text')}({ctx.input('path')})"
        ctx.output("text", text)
        ctx.output("lines", f"{text}.splitlines()")


class SNA_Node_WriteTextFile(ScriptingBaseNode, bpy.types.Node):
    """Write text to a file, replacing it or adding to its end. Missing
    folders are created."""

    bl_idname = "SNA_Node_WriteTextFile"
    bl_label = "Write Text File"
    sn_permissions = FILES
    sn_inputs = [Flow(), String("path", "Path"), String("text", "Text")]
    sn_outputs = [Flow("next")]

    append: bpy.props.BoolProperty(
        name="Add to End", description="Keep the file's text and add to it"
    )

    def draw(self, context, layout):
        layout.prop(self, "append")

    def emit(self, ctx):
        args = [ctx.input("path"), ctx.input("text")]
        if self.append:
            args.append("append=True")
        ctx.code(f"""
            {ctx.helper("sn_write_text")}({", ".join(args)})
            {ctx.flow("next")}
        """)


class SNA_Node_CreateFolder(ScriptingBaseNode, bpy.types.Node):
    """Create a folder (and the folders above it) if it doesn't exist."""

    bl_idname = "SNA_Node_CreateFolder"
    bl_label = "Create Folder"
    sn_permissions = FILES
    sn_inputs = [Flow(), String("path", "Path")]
    sn_outputs = [Flow("next")]

    def emit(self, ctx):
        ctx.imports("import os")
        ctx.code(f"""
            os.makedirs(bpy.path.abspath({ctx.input("path")}), exist_ok=True)
            {ctx.flow("next")}
        """)


class SNA_Node_ListFolder(ScriptingBaseNode, bpy.types.Node):
    """The files and/or folders in a folder, sorted by name."""

    bl_idname = "SNA_Node_ListFolder"
    bl_label = "List Folder"
    sn_permissions = FILES
    sn_header_props = ("kind",)

    kind: bpy.props.EnumProperty(
        name="List",
        items=[
            ("FILES", "Files", "Only files"),
            ("FOLDERS", "Folders", "Only folders"),
            ("BOTH", "Files and Folders", "Both"),
        ],
    )
    full_paths: bpy.props.BoolProperty(
        name="Full Paths", description="Paths instead of only the names", default=True
    )

    def socket_specs(self):
        inputs = [
            String("folder", "Folder"),
            String("extension", "Extension", enabled=self.kind != "FOLDERS"),
        ]
        return inputs, [List("paths", "Paths")]

    def draw(self, context, layout):
        layout.prop(self, "full_paths")

    def emit(self, ctx):
        args = [ctx.input("folder")]
        if self.kind != "FOLDERS":
            args.append(ctx.input("extension"))
        else:
            args.append('""')
        if self.kind != "FILES":
            args.append(repr(self.kind))
        if not self.full_paths:
            args.append("full_paths=False")
        ctx.output("paths", f"{ctx.helper('sn_list_folder')}({', '.join(args)})")


class SNA_Node_JoinPath(ScriptingBaseNode, bpy.types.Node):
    """Join folder and file names into one path, with the right separator."""

    bl_idname = "SNA_Node_JoinPath"
    bl_label = "Join Path"
    sn_inputs = [String("first", "Path"), String("part", "Path", dynamic=True)]
    sn_outputs = [String("path", "Path")]

    def emit(self, ctx):
        ctx.imports("import os")
        parts = [ctx.input("first"), *ctx.inputs("part")]
        ctx.output("path", f"os.path.join({', '.join(parts)})")


class SNA_Node_PathInfo(ScriptingBaseNode, bpy.types.Node):
    """The parts of a path, and whether it exists. // paths are turned into
    full paths first."""

    bl_idname = "SNA_Node_PathInfo"
    bl_label = "Path Info"
    sn_permissions = FILES
    sn_inputs = [String("path", "Path")]
    sn_outputs = [
        String("absolute", "Full Path"),
        String("folder", "Folder"),
        String("file_name", "File Name"),
        String("name", "Name"),
        String("extension", "Extension"),
        Boolean("exists", "Exists"),
        Boolean("is_file", "Is File"),
        Boolean("is_folder", "Is Folder"),
    ]

    def emit(self, ctx):
        ctx.imports("import os")
        path = f"bpy.path.abspath({ctx.input('path')})"
        ctx.output("absolute", path)
        ctx.output("folder", f"os.path.dirname({path})")
        ctx.output("file_name", f"os.path.basename({path})")
        ctx.output("name", f"os.path.splitext(os.path.basename({path}))[0]")
        ctx.output("extension", f"os.path.splitext({path})[1]")
        ctx.output("exists", f"os.path.exists({path})")
        ctx.output("is_file", f"os.path.isfile({path})")
        ctx.output("is_folder", f"os.path.isdir({path})")


DATA_TYPES = [
    (name, name.replace("_", " ").title(), "", i)
    for i, name in enumerate(
        (
            "objects", "collections", "materials", "node_groups", "meshes",
            "worlds", "images", "texts", "actions", "brushes", "cameras",
            "lights", "curves", "fonts", "grease_pencils", "palettes",
            "scenes", "textures", "armatures",
        )
    )
]  # fmt: skip


class SNA_Node_LoadFromBlend(ScriptingBaseNode, bpy.types.Node):
    """Append or link data from a .blend file: the given names, everything
    of the type without. Objects and collections can be added to the scene."""

    bl_idname = "SNA_Node_LoadFromBlend"
    bl_label = "Load from Blend File"
    sn_permissions = FILES
    sn_header_props = ("data_type",)
    sn_inputs = [Flow(), String("path", "Blend File"), String("names", "Names")]
    sn_outputs = [Flow("next"), List("loaded", "Loaded")]

    data_type: bpy.props.EnumProperty(name="Type", items=DATA_TYPES)
    link: bpy.props.BoolProperty(
        name="Link", description="Link instead of append (stays in the other file)"
    )
    add_to_scene: bpy.props.BoolProperty(
        name="Add to Scene",
        description="Put loaded objects and collections in the scene",
    )

    def draw(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "link", toggle=True)
        sub = row.row(align=True)
        sub.enabled = self.data_type in ("objects", "collections")
        sub.prop(self, "add_to_scene", toggle=True)

    def emit(self, ctx):
        loaded = ctx.var("loaded")
        args = [ctx.input("path"), repr(self.data_type), ctx.input("names")]
        if self.link:
            args.append("link=True")
        if self.add_to_scene and self.data_type in ("objects", "collections"):
            args.append("add_to_scene=True")
        ctx.output("loaded", loaded)
        ctx.code(f"""
            {loaded} = {ctx.helper("sn_load_blend")}({", ".join(args)})
            {ctx.flow("next")}
        """)


class SNA_Node_BlendFileContents(ScriptingBaseNode, bpy.types.Node):
    """The names of the data of a type in a .blend file (without loading
    it), e.g. to offer its materials in a list."""

    bl_idname = "SNA_Node_BlendFileContents"
    bl_label = "Blend File Contents"
    sn_permissions = FILES
    sn_header_props = ("data_type",)
    sn_inputs = [String("path", "Blend File")]
    sn_outputs = [List("names", "Names")]

    data_type: bpy.props.EnumProperty(name="Type", items=DATA_TYPES)

    def emit(self, ctx):
        helper = ctx.helper("sn_blend_contents")
        ctx.output("names", f"{helper}({ctx.input('path')}, {self.data_type!r})")
