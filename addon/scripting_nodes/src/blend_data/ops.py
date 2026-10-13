"""Getting Blender data paths into the node editor: paste a copied path, and
"Copy Data Path for Scripting Nodes" in the right-click menu of every
property in Blender."""

import bpy

from ..lib.trees import node_by_id
from ..node_tree.node_tree import ScriptingNodeTree
from . import explorer, rna


class SNA_OT_PasteBlenderPath(bpy.types.Operator):
    """Set the path from a copied data path (right-click a property > Copy Data Path for Scripting Nodes, or Copy Full Data Path)"""

    bl_idname = "sna.paste_blender_path"
    bl_label = "Paste Data Path"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    # the node to set up; empty adds a new Blender Data node
    node_id: bpy.props.StringProperty(options={"SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (
            space is not None
            and space.type == "NODE_EDITOR"
            and space.edit_tree is not None
            and space.edit_tree.bl_idname == ScriptingNodeTree.bl_idname
        )

    def execute(self, context):
        text = context.window_manager.clipboard
        try:
            rna.parse(text)
        except ValueError as error:
            self.report({"WARNING"}, str(error))
            return {"CANCELLED"}

        node = node_by_id(self.node_id)
        added = node is None
        if added:
            tree = context.space_data.edit_tree
            node = tree.nodes.new("SNA_Node_BlendData")
            node.location = context.space_data.cursor_location
            for other in tree.nodes:
                other.select = other == node
            tree.nodes.active = node
        node.paste_path(text, context)
        if added:
            bpy.ops.transform.translate("INVOKE_DEFAULT")
        return {"FINISHED"}


NO_TYPE = "__NONE__"
# enum items must stay alive while Blender shows them
_type_items_cache = {}


def _type_items(self, context):
    node = node_by_id(self.node_id)
    if node is None:
        names = ()
        none_label = ""
    elif self.target == "CAST":
        base = node.path_final(cast=False).rna_type
        names = rna.subtypes(base)
        none_label = rna.display_name(base)
    else:
        names = tuple(rna.all_types())
        none_label = "Any"
    key = (none_label, names)
    if key not in _type_items_cache:
        items = [(NO_TYPE, none_label or "None", "")]
        items += [(name, rna.display_name(name), name) for name in names]
        _type_items_cache[key] = items
    return _type_items_cache[key]


class SNA_OT_BlendPathType(bpy.types.Operator):
    """Pick the type of this Blender data"""

    bl_idname = "sna.blend_path_type"
    bl_label = "Data Type"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    bl_property = "type_name"

    node_id: bpy.props.StringProperty(options={"SKIP_SAVE"})
    # CAST: a more specific type of the result, INPUT: the type of the input
    target: bpy.props.EnumProperty(
        items=[("CAST", "Cast", ""), ("INPUT", "Input", "")], options={"SKIP_SAVE"}
    )
    type_name: bpy.props.EnumProperty(items=_type_items)

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        node = node_by_id(self.node_id)
        if node is None:
            return {"CANCELLED"}
        value = "" if self.type_name == NO_TYPE else self.type_name
        setattr(
            node, "path_cast" if self.target == "CAST" else "path_input_type", value
        )
        return {"FINISHED"}


class SNA_OT_CopyBlenderPath(bpy.types.Operator):
    """Copy the path of this property to paste it into Scripting Nodes"""

    bl_idname = "sna.copy_blender_path"
    bl_label = "Copy Data Path for Scripting Nodes"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        pointer = getattr(context, "button_pointer", None)
        prop = getattr(context, "button_prop", None)
        if pointer is None or prop is None:
            self.report({"WARNING"}, "This isn't a property")
            return {"CANCELLED"}
        wm = context.window_manager
        path = ""
        if bpy.ops.ui.copy_data_path_button.poll():
            bpy.ops.ui.copy_data_path_button(full_path=True)
            path = wm.clipboard
        try:
            parsed = rna.parse(path)
            # a vector property copies the component that was clicked
            if parsed.keys and parsed.segments[-2:] == [prop.identifier, rna.SUBSCRIPT]:
                path = path[: path.rindex("[")]
        except ValueError:
            # no full path (tool settings, editor settings, ...): start at
            # data of the owner's type, connected in the node editor
            path = f"bpy.types.{pointer.bl_rna.identifier}.{prop.identifier}"
        wm.clipboard = path
        self.report({"INFO"}, f"Copied {path}")
        return {"FINISHED"}


# -----------------------------------------------------------------------------
# Data explorer (blend_data/explorer.py, ui/explorer_panel.py)
# -----------------------------------------------------------------------------


def explorer_node(context):
    """The node the explorer follows, or None."""
    if not context.scene.sna.ui.explorer_follow:
        return None
    tree = getattr(context.space_data, "edit_tree", None)
    node = tree.nodes.active if tree is not None else None
    return node if node is not None and explorer.follows(node) else None


def explorer_location(context):
    node = explorer_node(context)
    if node is not None:
        return node, explorer.node_location(node, context)
    return None, explorer.free_location(context.scene.sna.ui.explorer_path)


class _ExplorerTarget:
    """Where to go from the current location: an attribute (`member`), an
    item of a collection (`item_mode`), or a root (`root`)."""

    member: bpy.props.StringProperty(options={"SKIP_SAVE"})
    item_mode: bpy.props.EnumProperty(
        items=[("", "None", ""), ("INDEX", "Index", ""), ("NAME", "Name", ""), ("ACTIVE", "Active", "")],
        options={"SKIP_SAVE"},
    )  # fmt: skip
    item_name: bpy.props.StringProperty(options={"SKIP_SAVE"})
    item_index: bpy.props.IntProperty(options={"SKIP_SAVE"})
    root: bpy.props.StringProperty(options={"SKIP_SAVE"})

    def target(self, location):
        if self.root:
            return explorer.Location(self.root)
        if self.item_mode:
            value = self.item_name if self.item_mode == "NAME" else self.item_index
            key = explorer.Key(
                self.item_mode, None if self.item_mode == "ACTIVE" else value
            )
            return location.extended(key=key)
        return location.extended(self.member)


def _go(context, node, location):
    ui = context.scene.sna.ui
    ui.explorer_filter = ""
    if node is not None:
        explorer.set_node_location(node, location)
    elif location.root:
        ui.explorer_path = location.python()
    else:
        ui.explorer_path = ""


class SNA_OT_ExplorerOpen(_ExplorerTarget, bpy.types.Operator):
    """Go into this entry (changes the path of the followed node)"""

    bl_idname = "sna.explorer_open"
    bl_label = "Open"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        node, location = explorer_location(context)
        _go(context, node, self.target(location))
        return {"FINISHED"}


class SNA_OT_ExplorerBack(bpy.types.Operator):
    """Go back to this step"""

    bl_idname = "sna.explorer_back"
    bl_label = "Back"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    # segments to keep; -1: the list of roots
    count: bpy.props.IntProperty(options={"SKIP_SAVE"})

    def execute(self, context):
        node, location = explorer_location(context)
        target = (
            explorer.Location("") if self.count < 0 else location.truncated(self.count)
        )
        _go(context, node, target)
        return {"FINISHED"}


class SNA_OT_ExplorerAdd(_ExplorerTarget, bpy.types.Operator):
    """Add a Blender Data node for this entry"""

    bl_idname = "sna.explorer_add"
    bl_label = "Add Node"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        return SNA_OT_PasteBlenderPath.poll(context)

    def execute(self, context):
        tree = context.space_data.edit_tree
        followed, location = explorer_location(context)
        target = self.target(location)
        node = tree.nodes.new("SNA_Node_BlendData")
        if followed is not None and followed.bl_idname == "SNA_Node_BlendData":
            # continue from the followed node: Input + the new step
            node.location = (
                followed.location.x + followed.width + 60,
                followed.location.y,
            )
            node.path_root = "INPUT"
            tree.links.new(followed.outputs[0], node.socket("data"))
            step = explorer.Location("INPUT", target.parts[len(location.parts):],
                                     target.keys[len(location.keys):])  # fmt: skip
            explorer.set_node_location(node, step)
        else:
            if followed is not None:
                node.location = (followed.location.x, followed.location.y - 250)
                data = followed.socket("data")
                if target.root == "INPUT" and data is not None and data.is_linked:
                    tree.links.new(data.links[0].from_socket, node.socket("data"))
            else:
                node.location = _view_center(context)
            node.path_root = target.root
            explorer.set_node_location(node, target)
        for other in tree.nodes:
            other.select = other == node
        tree.nodes.active = node
        tree.update()
        return {"FINISHED"}


def _view_center(context):
    region = next((r for r in context.area.regions if r.type == "WINDOW"), None)
    if region is None:
        return (0, 0)
    return region.view2d.region_to_view(region.width / 2, region.height / 2)


def _button_context_menu(self, context):
    if getattr(context, "button_prop", None) is None:
        return
    if getattr(context, "button_pointer", None) is None:
        return
    layout = self.layout
    layout.separator()
    layout.operator(SNA_OT_CopyBlenderPath.bl_idname, icon="NODETREE")


def register():
    bpy.types.UI_MT_button_context_menu.append(_button_context_menu)


def unregister():
    bpy.types.UI_MT_button_context_menu.remove(_button_context_menu)
