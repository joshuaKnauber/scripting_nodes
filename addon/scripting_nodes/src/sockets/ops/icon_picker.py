import bpy

from ...lib.icons import builtin_icons

_items = []


def _icon_items(self, context):
    if not _items:  # Blender keeps pointers into the list: build it once
        _items.append(("NONE", "None", "No icon", "NONE", 0))
        for i, name in enumerate(builtin_icons()):
            if name != "NONE":
                label = name.replace("_", " ").title()
                _items.append((name, label, name, name, i + 1))
    return _items


class SNA_OT_PickIcon(bpy.types.Operator):
    """Pick a built-in icon"""

    bl_idname = "sna.pick_icon"
    bl_label = "Icon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    bl_property = "icon"

    prop_name: bpy.props.StringProperty(options={"SKIP_SAVE"})
    icon: bpy.props.EnumProperty(items=_icon_items)

    # where the picked name goes: the owner (socket, node, list item) by its
    # data-block and path, found again when the search popup returns
    id_type: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    id_name: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def invoke(self, context, event):
        owner = getattr(context, "sna_icon_owner", None)
        if owner is None:
            return {"CANCELLED"}
        data = owner.id_data
        self.id_type = "SCENE" if isinstance(data, bpy.types.Scene) else "NODETREE"
        self.id_name = data.name
        self.path = owner.path_from_id()
        context.window_manager.invoke_search_popup(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        ids = bpy.data.scenes if self.id_type == "SCENE" else bpy.data.node_groups
        data = ids.get(self.id_name)
        if data is None:
            return {"CANCELLED"}
        owner = data.path_resolve(self.path) if self.path else data
        setattr(owner, self.prop_name, "" if self.icon == "NONE" else self.icon)
        return {"FINISHED"}
