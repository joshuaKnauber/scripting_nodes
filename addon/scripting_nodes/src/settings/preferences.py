import bpy
from bpy.types import AddonPreferences


# the add-on's package (this module is in <package>.src.settings)
_addon_name = __package__.rsplit(".src.", 1)[0]


class SNA_AddonPreferences(AddonPreferences):
    """Scripting Nodes addon preferences"""

    bl_idname = _addon_name

    mcp_port: bpy.props.IntProperty(
        name="MCP Server Port",
        description="TCP port the MCP server listens on (localhost only)",
        default=7423,
        min=1024,
        max=65535,
    )

    mcp_autostart: bpy.props.BoolProperty(
        name="Start with Blender",
        description="Start the MCP server when Blender starts",
    )
    mcp_allow_python: bpy.props.BoolProperty(
        name="Allow Running Python",
        description=(
            "Let MCP clients run Python in Blender (run_python). Any program "
            "on this computer that can reach the port could then run code"
        ),
        default=True,
    )
    mcp_token: bpy.props.StringProperty(
        name="Token",
        description=(
            "Optional: clients must send it (Authorization: Bearer <token>). "
            "Read when the server starts"
        ),
        subtype="PASSWORD",
    )

    def draw(self, context):
        layout = self.layout
        draw_node_packages(layout.box())

        box = layout.box()
        box.label(text="MCP Server", icon="PLUGIN")
        col = box.column()
        col.use_property_split = True
        col.prop(self, "mcp_port")
        col.prop(self, "mcp_autostart")
        col.prop(self, "mcp_allow_python")
        col.prop(self, "mcp_token")
        col.label(
            text="Start/stop the server from the node editor sidebar (N panel).",
            icon="INFO",
        )


def draw_node_packages(layout):
    """Installed node packages (core/node_packages.py)."""
    from ..core import node_packages

    row = layout.row()
    row.label(text="Node Packages", icon="NODETREE")
    row.operator("sna.install_node_package", icon="IMPORT")
    row.operator(
        "wm.path_open", text="", icon="FILE_FOLDER"
    ).filepath = node_packages.install_folder()
    installed = list(node_packages.packages.values())
    if not installed:
        col = layout.column(align=True)
        col.active = False
        col.label(text="Zips of extra nodes. They run Python like add-ons:")
        col.label(text="install only packages you trust.")
        return
    for package in installed:
        box = layout.box()
        row = box.row()
        details = " ".join(p for p in (package.version, package.author) if p)
        row.label(text=f"{package.name}  {details}".strip(), icon="PACKAGE")
        sub = row.row()
        sub.active = False
        count = len(package.nodes)
        sub.label(text=f"{count} node{'s' if count != 1 else ''}")
        row.operator(
            "sna.remove_node_package", text="", icon="TRASH"
        ).package_id = package.id
        if package.error:
            col = box.column(align=True)
            col.alert = True
            col.label(text=package.error, icon="ERROR")


class SNA_OT_InstallNodePackage(bpy.types.Operator):
    """Install a zip of extra nodes (its Python runs like an add-on's: only
    install packages you trust)"""

    bl_idname = "sna.install_node_package"
    bl_label = "Install"
    bl_options = {"REGISTER", "INTERNAL"}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.zip", options={"HIDDEN"})

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        from ..core import node_packages

        try:
            package = node_packages.install(self.filepath)
        except node_packages.InstallError as exc:
            self.report({"ERROR"}, f"Can't install: {exc}")
            return {"CANCELLED"}
        self.report({"INFO"}, f"Installed {package.name}, reloading Scripting Nodes")
        node_packages.reload()
        return {"FINISHED"}


class SNA_OT_RemoveNodePackage(bpy.types.Operator):
    """Remove the node package (nodes of it in your files show as missing)"""

    bl_idname = "sna.remove_node_package"
    bl_label = "Remove Node Package"
    bl_options = {"REGISTER", "INTERNAL"}

    package_id: bpy.props.StringProperty(options={"HIDDEN"})

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        from ..core import node_packages

        try:
            node_packages.remove(self.package_id)
        except node_packages.InstallError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        node_packages.reload()
        return {"FINISHED"}


def get_preferences() -> SNA_AddonPreferences:
    """Get the addon preferences"""
    return bpy.context.preferences.addons[_addon_name].preferences
