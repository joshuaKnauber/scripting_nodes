"""Property definitions: the add-on's properties (Addon Data sidebar) and the
properties of Operator / Preferences nodes, as lists.

    scene.sna.addon.properties   add-on properties and groups
    group.members                properties of a group (type GROUP)
    node.properties              properties of an Operator / Preferences node

Nodes only use properties (Get / Set Property, fields, On Property Update),
picking them by `id`. Code is generated in core/properties.py.
"""

import bpy

from ..core import scheduler
from ..core.properties import picker_attr, reference
from ..lib.ids import get_short_id

PROPERTY_TYPES = [
    ("BOOLEAN", "Boolean", "True or False (checkbox)", "CHECKBOX_HLT", 0),
    ("INTEGER", "Integer", "A whole number", "CON_TRANSFORM", 1),
    ("FLOAT", "Float", "A decimal number", "CON_TRANSLIKE", 2),
    ("VECTOR", "Vector", "2 to 4 decimal numbers, e.g. a location or a color", "EMPTY_AXIS", 3),
    ("STRING", "String", "Text, a file path, ...", "SYNTAX_OFF", 4),
    ("ENUM", "Enum", "One of a list of items (dropdown)", "PRESET", 5),
    ("POINTER", "Pointer", "A Blender data-block or a group", "OBJECT_DATAMODE", 6),
    ("COLLECTION", "Collection", "A list of group items", "OUTLINER_COLLECTION", 7),
    ("GROUP", "Group", "Properties used together as the type of Pointer and Collection properties", "OUTLINER_DATA_POINTCLOUD", 8),
]  # fmt: skip
TYPE_ICONS = {item[0]: item[3] for item in PROPERTY_TYPES}

ATTACH_TYPES = [
    ("Scene", "Scene", "One value per scene (context.scene)", "SCENE_DATA", 0),
    ("Object", "Object", "One value per object (context.object)", "OBJECT_DATA", 1),
    ("WindowManager", "Window Manager", "One value per session, not saved (context.window_manager)", "WINDOW", 2),
    ("Mesh", "Mesh", "One value per mesh", "MESH_DATA", 3),
    ("Material", "Material", "One value per material (context.material)", "MATERIAL", 4),
    ("Collection", "Collection", "One value per collection (context.collection)", "OUTLINER_COLLECTION", 5),
    ("World", "World", "One value per world", "WORLD", 6),
    ("Camera", "Camera", "One value per camera", "CAMERA_DATA", 7),
    ("Light", "Light", "One value per light", "LIGHT", 8),
    ("Armature", "Armature", "One value per armature", "ARMATURE_DATA", 9),
    ("Image", "Image", "One value per image", "IMAGE_DATA", 10),
    ("NodeTree", "Node Tree", "One value per node tree", "NODETREE", 11),
    ("Text", "Text", "One value per text", "TEXT", 12),
]  # fmt: skip

POINTER_TYPES = [
    (t, t if t != "NodeTree" else "Node Tree", "")
    for t in (
        "Object", "Mesh", "Material", "Image", "Texture", "NodeTree", "Collection",
        "Camera", "Light", "World", "Armature", "Curve", "Lattice", "GreasePencil",
        "Text", "Action", "Brush", "Scene", "Sound", "Font", "MovieClip",
    )
]  # fmt: skip

INT_SUBTYPES = [
    ("NONE", "None", ""), ("PIXEL", "Pixel", ""), ("UNSIGNED", "Unsigned", ""),
    ("PERCENTAGE", "Percentage", ""), ("FACTOR", "Factor", ""),
    ("TIME", "Time", "Frames"), ("TIME_ABSOLUTE", "Time Absolute", ""),
]  # fmt: skip
FLOAT_SUBTYPES = [
    ("NONE", "None", ""), ("PIXEL", "Pixel", ""), ("UNSIGNED", "Unsigned", ""),
    ("PERCENTAGE", "Percentage", ""), ("FACTOR", "Factor", "0 to 1"),
    ("ANGLE", "Angle", ""), ("TIME", "Time", ""), ("TIME_ABSOLUTE", "Time Absolute", ""),
    ("DISTANCE", "Distance", ""), ("DISTANCE_CAMERA", "Camera Distance", ""),
    ("POWER", "Power", ""), ("TEMPERATURE", "Temperature", ""),
]  # fmt: skip
VECTOR_SUBTYPES = [
    ("NONE", "None", ""), ("COLOR", "Color", ""), ("COLOR_GAMMA", "Color Gamma", ""),
    ("TRANSLATION", "Translation", ""), ("DIRECTION", "Direction", ""),
    ("VELOCITY", "Velocity", ""), ("ACCELERATION", "Acceleration", ""),
    ("EULER", "Euler", ""), ("QUATERNION", "Quaternion", ""),
    ("AXISANGLE", "Axis Angle", ""), ("XYZ", "XYZ", ""),
]  # fmt: skip
STRING_SUBTYPES = [
    ("NONE", "None", ""), ("FILE_PATH", "File Path", ""), ("DIR_PATH", "Directory Path", ""),
    ("FILE_NAME", "File Name", ""), ("BYTE_STRING", "Byte String", ""),
    ("PASSWORD", "Password", ""),
]  # fmt: skip
FLOAT_UNITS = [
    ("NONE", "None", ""), ("LENGTH", "Length", ""), ("AREA", "Area", ""),
    ("VOLUME", "Volume", ""), ("ROTATION", "Rotation", ""), ("TIME", "Time", ""),
    ("VELOCITY", "Velocity", ""), ("ACCELERATION", "Acceleration", ""),
    ("MASS", "Mass", ""), ("CAMERA", "Camera", ""), ("POWER", "Power", ""),
    ("TEMPERATURE", "Temperature", ""),
]  # fmt: skip

INT_MIN, INT_MAX = -(2**31), 2**31 - 1
FLOAT_MAX = 3.4e38


def _changed(self, context):
    scheduler.request_full()


def _function_poll(self, tree):
    from ..core import functions

    return tree.bl_idname == "ScriptingNodeTree" and functions.is_function(tree)


def _p(prop, *args, **kwargs):
    """A setting that rebuilds the add-on when it changes."""
    return prop(*args, update=_changed, **kwargs)


class SNA_EnumItem(bpy.types.PropertyGroup):
    name: _p(bpy.props.StringProperty, name="Name", default="Item")
    identifier: _p(
        bpy.props.StringProperty,
        name="Identifier",
        description="Value in code (defaults to the name)",
    )
    description: _p(bpy.props.StringProperty, name="Description")
    icon: _p(bpy.props.StringProperty, name="Icon")

    @property
    def value(self):
        return self.identifier or self.name


class PropertySettings:
    """Everything a property definition stores. `name` (the label) comes from
    PropertyGroup."""

    id: bpy.props.StringProperty(options={"HIDDEN"})
    property_type: _p(bpy.props.EnumProperty, items=PROPERTY_TYPES, name="Type")
    description: _p(bpy.props.StringProperty, name="Description")
    python_name: _p(
        bpy.props.StringProperty,
        name="Python Name",
        description=(
            "Name in code (optional, defaults to the name). Saved values are "
            "stored under it: set it to keep them when you rename the property"
        ),
    )

    # options
    option_hidden: _p(bpy.props.BoolProperty, name="Hidden")
    option_skip_save: _p(bpy.props.BoolProperty, name="Skip Save")
    option_animatable: _p(bpy.props.BoolProperty, name="Animatable", default=True)
    option_library_editable: _p(bpy.props.BoolProperty, name="Library Editable")

    # BOOLEAN
    default_bool: _p(bpy.props.BoolProperty, name="Default")
    # INTEGER
    default_int: _p(bpy.props.IntProperty, name="Default")
    subtype_int: _p(bpy.props.EnumProperty, items=INT_SUBTYPES, name="Subtype")
    # FLOAT / VECTOR
    default_float: _p(bpy.props.FloatProperty, name="Default")
    default_vector: _p(bpy.props.FloatVectorProperty, name="Default", size=4)
    vector_size: _p(bpy.props.IntProperty, name="Size", default=3, min=2, max=4)
    subtype_float: _p(bpy.props.EnumProperty, items=FLOAT_SUBTYPES, name="Subtype")
    subtype_vector: _p(bpy.props.EnumProperty, items=VECTOR_SUBTYPES, name="Subtype")
    unit: _p(bpy.props.EnumProperty, items=FLOAT_UNITS, name="Unit")
    precision: _p(bpy.props.IntProperty, name="Precision", default=3, min=0, max=6)
    # limits (INTEGER, FLOAT, VECTOR)
    use_min: _p(bpy.props.BoolProperty, name="Min")
    use_max: _p(bpy.props.BoolProperty, name="Max")
    use_soft_limits: _p(bpy.props.BoolProperty, name="Soft Limits")
    min_value: _p(bpy.props.FloatProperty, name="Min")
    max_value: _p(bpy.props.FloatProperty, name="Max", default=1.0)
    soft_min: _p(bpy.props.FloatProperty, name="Soft Min")
    soft_max: _p(bpy.props.FloatProperty, name="Soft Max", default=1.0)
    # STRING
    default_string: _p(bpy.props.StringProperty, name="Default")
    subtype_string: _p(bpy.props.EnumProperty, items=STRING_SUBTYPES, name="Subtype")
    maxlen: _p(bpy.props.IntProperty, name="Max Length", min=0)
    # ENUM
    enum_items: bpy.props.CollectionProperty(type=SNA_EnumItem)
    active_enum_item: bpy.props.IntProperty()
    default_enum: _p(
        bpy.props.StringProperty,
        name="Default",
        description="Identifier of the default item (empty: the first)",
    )
    enum_flag: _p(
        bpy.props.BoolProperty,
        name="Multiple",
        description="Allow selecting several items (a set)",
    )
    items_function: _p(
        bpy.props.PointerProperty,
        type=bpy.types.NodeTree,
        name="Items Function",
        description=(
            "Function returning the items (a list of names or of "
            "(identifier, name, description) tuples), called when the dropdown "
            "opens. Empty: the items listed here"
        ),
        poll=_function_poll,
    )
    # POINTER / COLLECTION
    pointer_source: _p(
        bpy.props.EnumProperty,
        name="Points To",
        items=[
            ("BLENDER", "Blender Data", "A data-block such as an object or material"),
            ("GROUP", "Group", "A group of this add-on"),
        ],
    )
    pointer_type: _p(bpy.props.EnumProperty, items=POINTER_TYPES, name="Data Type")
    group: reference(
        "group", "GROUP", name="Group", description="Group used as the type"
    )
    group_id: _p(bpy.props.StringProperty, options={"HIDDEN"})
    poll_function: _p(
        bpy.props.PointerProperty,
        type=bpy.types.NodeTree,
        name="Poll Function",
        description=(
            "Function deciding which data-blocks can be picked: gets the "
            "data-block as first input, returns True to allow it"
        ),
        poll=_function_poll,
    )

    @property
    def uses_group(self):
        return self.property_type == "COLLECTION" or (
            self.property_type == "POINTER" and self.pointer_source == "GROUP"
        )

    def init(self, name, property_type="FLOAT"):
        self.id = get_short_id()
        self.name = name
        self.property_type = property_type
        if property_type == "ENUM":
            for item_name in ("Option A", "Option B"):
                self.enum_items.add().name = item_name


class SNA_PropertyMember(PropertySettings, bpy.types.PropertyGroup):
    """A property of a group or of an Operator / Preferences node."""


class SNA_Property(PropertySettings, bpy.types.PropertyGroup):
    """An add-on property (or group)."""

    attach_to: _p(
        bpy.props.EnumProperty,
        items=ATTACH_TYPES,
        name="Attach To",
        description="Data the property is stored on",
    )
    in_addon_group: _p(
        bpy.props.BoolProperty,
        name="In Add-on Group",
        description=(
            "Store it in the add-on's group (scene.my_addon.count) instead of "
            "directly on the data (scene.count)"
        ),
        default=True,
    )
    members: bpy.props.CollectionProperty(type=SNA_PropertyMember)
    active_member: bpy.props.IntProperty()


# -----------------------------------------------------------------------------
# Lists: where a list lives is described by (owner kind, owner id)
#   ADDON  -  scene.sna.addon.properties
#   GROUP  <group id>  - that group's members
#   NODE   <node id>   - an Operator / Preferences node's properties
# -----------------------------------------------------------------------------


def get_list(owner, owner_id=""):
    """(collection, data holding it, its attribute, index attribute)."""
    addon = bpy.context.scene.sna.addon
    if owner == "ADDON":
        return addon.properties, addon, "properties", "active_property"
    if owner == "GROUP":
        group = next((p for p in addon.properties if p.id == owner_id), None)
        if group is not None:
            return group.members, group, "members", "active_member"
    if owner == "NODE":
        from ..lib.trees import node_by_id

        node = node_by_id(owner_id)
        if node is not None and hasattr(node, "properties"):
            return node.properties, node, "properties", "active_property"
    return None, None, "", ""


class _ListOperator:
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    owner: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})
    owner_id: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    def execute(self, context):
        items, data, _, index_attr = get_list(self.owner, self.owner_id)
        if items is None:
            return {"CANCELLED"}
        self.apply(items, data, index_attr)
        scheduler.request_full()
        return {"FINISHED"}


class SNA_OT_AddProperty(_ListOperator, bpy.types.Operator):
    """Add a property"""

    bl_idname = "sna.add_property"
    bl_label = "Add Property"

    def apply(self, items, data, index_attr):
        names = {item.name for item in items}
        name, i = "Property", 2
        while name in names:
            name, i = f"Property {i}", i + 1
        items.add().init(name)
        setattr(data, index_attr, len(items) - 1)


class SNA_OT_RemoveProperty(_ListOperator, bpy.types.Operator):
    """Remove the selected property"""

    bl_idname = "sna.remove_property"
    bl_label = "Remove Property"

    def apply(self, items, data, index_attr):
        index = getattr(data, index_attr)
        if 0 <= index < len(items):
            items.remove(index)
            setattr(data, index_attr, min(index, len(items) - 1))


class SNA_OT_MoveProperty(_ListOperator, bpy.types.Operator):
    """Move the selected property"""

    bl_idname = "sna.move_property"
    bl_label = "Move Property"

    direction: bpy.props.EnumProperty(items=[("UP", "Up", ""), ("DOWN", "Down", "")])

    def apply(self, items, data, index_attr):
        index = getattr(data, index_attr)
        target = index - 1 if self.direction == "UP" else index + 1
        if 0 <= index < len(items) and 0 <= target < len(items):
            items.move(index, target)
            setattr(data, index_attr, target)


class SNA_OT_EnumItemAdd(bpy.types.Operator):
    """Add an item"""

    bl_idname = "sna.enum_item_add"
    bl_label = "Add Item"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    prop_id: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    def execute(self, context):
        from ..core.properties import find

        found = find(self.prop_id)
        if found is None:
            return {"CANCELLED"}
        items = found.prop.enum_items
        names = {item.name for item in items}
        name, i = "Item", 2
        while name in names:
            name, i = f"Item {i}", i + 1
        items.add().name = name
        found.prop.active_enum_item = len(items) - 1
        scheduler.request_full()
        return {"FINISHED"}


class SNA_OT_EnumItemRemove(bpy.types.Operator):
    """Remove the selected item"""

    bl_idname = "sna.enum_item_remove"
    bl_label = "Remove Item"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    prop_id: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    def execute(self, context):
        from ..core.properties import find

        found = find(self.prop_id)
        if found is None:
            return {"CANCELLED"}
        prop = found.prop
        if 0 <= prop.active_enum_item < len(prop.enum_items):
            prop.enum_items.remove(prop.active_enum_item)
            prop.active_enum_item = max(0, prop.active_enum_item - 1)
        scheduler.request_full()
        return {"FINISHED"}


# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------


class SNA_UL_Properties(bpy.types.UIList):
    bl_idname = "SNA_UL_Properties"

    def draw_item(self, context, layout, data, item, icon, active_data, prop):
        from ..core import errors

        row = layout.row(align=True)
        row.prop(
            item,
            "name",
            text="",
            emboss=False,
            icon=TYPE_ICONS.get(item.property_type, "DOT"),
        )
        if errors.property_errors.get(item.id):
            row.label(text="", icon="ERROR")


class SNA_UL_EnumItems(bpy.types.UIList):
    bl_idname = "SNA_UL_EnumItems"

    def draw_item(self, context, layout, data, item, icon, active_data, prop):
        layout.prop(item, "name", text="", emboss=False)


def draw_list(layout, owner, owner_id="", rows=4):
    """The list with add / remove / move buttons. Returns the active item."""
    items, data, list_attr, index_attr = get_list(owner, owner_id)
    if items is None:
        return None
    row = layout.row()
    row.template_list(
        "SNA_UL_Properties",
        f"{owner}_{owner_id}",
        data,
        list_attr,
        data,
        index_attr,
        rows=rows,
    )
    col = row.column(align=True)
    for operator, icon, extra in (
        ("sna.add_property", "ADD", None),
        ("sna.remove_property", "REMOVE", None),
        ("sna.move_property", "TRIA_UP", "UP"),
        ("sna.move_property", "TRIA_DOWN", "DOWN"),
    ):
        op = col.operator(operator, text="", icon=icon)
        op.owner, op.owner_id = owner, owner_id
        if extra:
            op.direction = extra
    index = getattr(data, index_attr)
    return items[index] if 0 <= index < len(items) else None


def draw_settings(layout, prop, top_level=False):
    """Settings of one property definition."""
    from ..core import errors

    layout.use_property_split = True
    layout.use_property_decorate = False
    error = errors.property_errors.get(prop.id)
    if error:
        box = layout.box()
        box.alert = True
        box.label(text=error, icon="ERROR")
    col = layout.column()
    col.prop(prop, "name")
    col.prop(prop, "property_type")
    kind = prop.property_type
    if kind == "GROUP":
        if top_level:
            layout.label(text="Properties")
            member = draw_list(layout, "GROUP", prop.id)
            if member is not None:
                draw_settings(layout.box(), member)
        else:
            layout.label(text="Groups can only be add-on properties", icon="ERROR")
        return
    if top_level:
        col.prop(prop, "attach_to")
        col.prop(prop, "in_addon_group")
    col.prop(prop, "description")

    col = layout.column()
    if kind == "BOOLEAN":
        col.prop(prop, "default_bool")
    elif kind == "INTEGER":
        col.prop(prop, "default_int")
        _draw_limits(col, prop)
        col.prop(prop, "subtype_int")
    elif kind == "FLOAT":
        col.prop(prop, "default_float")
        _draw_limits(col, prop)
        col.prop(prop, "precision")
        col.prop(prop, "subtype_float")
        col.prop(prop, "unit")
    elif kind == "VECTOR":
        col.prop(prop, "vector_size")
        sub = col.column(align=True)
        for i in range(prop.vector_size):
            sub.prop(prop, "default_vector", index=i, text="Default" if i == 0 else " ")
        _draw_limits(col, prop)
        col.prop(prop, "precision")
        col.prop(prop, "subtype_vector")
    elif kind == "STRING":
        col.prop(prop, "default_string")
        col.prop(prop, "subtype_string")
        col.prop(prop, "maxlen")
    elif kind == "ENUM":
        col.prop(prop, "items_function")
        if prop.items_function is None:
            row = layout.row()
            row.template_list(
                "SNA_UL_EnumItems",
                prop.id,
                prop,
                "enum_items",
                prop,
                "active_enum_item",
                rows=3,
            )
            sub = row.column(align=True)
            sub.operator("sna.enum_item_add", text="", icon="ADD").prop_id = prop.id
            sub.operator(
                "sna.enum_item_remove", text="", icon="REMOVE"
            ).prop_id = prop.id
            if 0 <= prop.active_enum_item < len(prop.enum_items):
                item = prop.enum_items[prop.active_enum_item]
                sub = layout.column()
                sub.prop(item, "identifier")
                sub.prop(item, "description")
                sub.prop(item, "icon")
            layout.prop(prop, "default_enum")
        layout.prop(prop, "enum_flag")
    elif kind in {"POINTER", "COLLECTION"}:
        if kind == "POINTER":
            col.prop(prop, "pointer_source")
        if prop.uses_group:
            col.prop_search(prop, "group", bpy.context.scene.sna, picker_attr("GROUP"))
        else:
            col.prop(prop, "pointer_type")
            col.prop(prop, "poll_function")

    col = layout.column(heading="Options")
    col.prop(prop, "option_hidden")
    col.prop(prop, "option_skip_save")
    if kind in {"BOOLEAN", "INTEGER", "FLOAT", "VECTOR", "STRING", "ENUM"}:
        col.prop(prop, "option_animatable")
    col.prop(prop, "option_library_editable")
    layout.prop(prop, "python_name")


def _draw_limits(col, prop):
    row = col.row(align=True, heading="Min")
    row.prop(prop, "use_min", text="")
    sub = row.row(align=True)
    sub.active = prop.use_min
    sub.prop(prop, "min_value", text="")
    row = col.row(align=True, heading="Max")
    row.prop(prop, "use_max", text="")
    sub = row.row(align=True)
    sub.active = prop.use_max
    sub.prop(prop, "max_value", text="")
    row = col.row(align=True, heading="Soft Limits")
    row.prop(prop, "use_soft_limits", text="")
    sub = row.row(align=True)
    sub.active = prop.use_soft_limits
    sub.prop(prop, "soft_min", text="")
    sub.prop(prop, "soft_max", text="")
