"""Nodes that follow a Blender data path: the Blender Data node and the
property nodes in Blender mode (nodes/_property_target.py).

A path starts at a root (the context, `bpy.data` or the node's Data input)
and is stored as segments, e.g. `objects[].modifiers[].show_viewport`. Every
`[]` gets an input for its key (index or name), or uses the collection's
active item. Types come from RNA (blend_data/rna.py), so outputs are typed
and the search only offers what exists on the type the path starts at.

    class SNA_Node_BlendData(BlendPathMixin, ScriptingBaseNode, bpy.types.Node):
        def socket_specs(self):
            final = self.path_final()
            return self.path_input_specs(), [rna.value_spec(final, "value", ...)]

        def emit(self, ctx):
            ctx.output("value", self.path_expression(ctx))
"""

import dataclasses

import bpy

from ..blend_data import rna
from ..core.context import NodeError
from ..sockets.data.socket_blend_data import linked_rna_type
from ..sockets.spec import Integer, String

ROOT_ITEMS = [
    ("CONTEXT", "Context", "Start at the current context (scene, active object, ...)", "WINDOW", 0),
    ("DATA", "Blend File", "Start at bpy.data (all objects, materials, ... of the file)", "FILE_BLEND", 1),
    ("INPUT", "Input", "Start at the connected data", "LINKED", 2),
]  # fmt: skip


def _key_update(self, context):
    # path_from_id() doesn't work for collection items of nodes
    pointer = self.as_pointer()
    for node in self.id_data.nodes:
        if any(key.as_pointer() == pointer for key in getattr(node, "path_keys", ())):
            node.mark_dirty()
            return


class SNA_BlendPathKey(bpy.types.PropertyGroup):
    """How one `[]` of a path picks an item."""

    mode: bpy.props.EnumProperty(
        name="Item",
        items=[
            ("INDEX", "Index", "Item at a position (0 is the first, -1 the last)"),
            ("NAME", "Name", "Item with a name"),
            ("ACTIVE", "Active", "The collection's active item"),
        ],
        update=_key_update,
    )


def _search_path(self, context, edit_text):
    results = rna.search(self.path_root_step(), edit_text, accept=self.path_accepts)
    return [(entry.path, f"{entry.text}   {entry.type_label}") for entry in results]


def _search_input_type(self, context, edit_text):
    text = edit_text.lower()
    return [name for name in rna.all_types() if text in name.lower()][:200]


def _search_cast(self, context, edit_text):
    final = self.path_final(cast=False)
    text = edit_text.lower()
    return [name for name in rna.subtypes(final.rna_type) if text in name.lower()]


class BlendPathMixin:
    path_root: bpy.props.EnumProperty(name="Start", items=ROOT_ITEMS, default="CONTEXT")
    path: bpy.props.StringProperty(
        name="Path",
        description="Search the data, or paste a copied data path",
        search=_search_path,
    )
    path_input_type: bpy.props.StringProperty(
        name="Input Type",
        description="Type of the data the path starts at, when the input doesn't tell",
        search=_search_input_type,
    )
    path_cast: bpy.props.StringProperty(
        name="As",
        description="Use the result as a more specific type (an object's data as Mesh, ...)",
        search=_search_cast,
    )
    path_keys: bpy.props.CollectionProperty(type=SNA_BlendPathKey)

    def path_accepts(self, step) -> bool:
        """Which final steps the search offers. Overridden by nodes that only
        work with some properties."""
        return True

    # -- resolution -----------------------------------------------------------

    def path_parts(self):
        """Segments of the path, or None if it isn't a valid path."""
        try:
            return rna.segments(self.path)
        except ValueError:
            return None

    def path_root_step(self):
        if self.path_root == "INPUT":
            type_name, collection = linked_rna_type(self.socket("data"))
            if not type_name:
                type_name, collection = self.path_input_type, False
            return rna.root_step(type_name, collection)
        return rna.root_step(rna.ROOT_TYPES[self.path_root])

    def path_steps(self):
        return rna.resolve(self.path_root_step(), self.path_parts() or [])

    def path_final(self, cast=True):
        """The step the whole path evaluates to."""
        steps = self.path_steps()
        final = steps[-1] if steps else self.path_root_step()
        if cast and self.path_cast and self.path_cast in rna.subtypes(final.rna_type):
            final = dataclasses.replace(final, rna_type=self.path_cast)
        return final

    def path_expression(self, ctx, count=None):
        """Code of the path (or of its first `count` segments)."""
        parts = self.path_parts()
        if parts is None:
            raise NodeError(f"Invalid data path: {self.path}")
        if self.path_root == "INPUT":
            if not ctx.is_linked("data"):
                raise NodeError("Connect the data the path starts at")
            expression = ctx.input("data")
        elif self.path_root == "CONTEXT":
            expression = ctx.context
        else:
            expression = rna.ROOT_EXPRESSIONS[self.path_root]

        owner = self.path_root_step()
        steps = rna.resolve(owner, parts)
        key = 0
        for part, step in list(zip(parts, steps))[:count]:
            if part != rna.SUBSCRIPT:
                expression = f"{expression}.{part}"
            else:
                mode = (
                    self.path_keys[key].mode if key < len(self.path_keys) else "INDEX"
                )
                if mode == "ACTIVE":
                    if owner.known and not rna.member(owner, "active").known:
                        raise NodeError(f"{rna.label(owner)} has no active item")
                    expression = f"{expression}.active"
                else:
                    expression = f"{expression}[{ctx.input(f'key_{key}')}]"
                key += 1
            owner = step
        return expression

    # -- sockets ---------------------------------------------------------------

    def sync_sockets(self):
        self._fit_path_keys()
        return super().sync_sockets()

    def _fit_path_keys(self):
        count = (self.path_parts() or []).count(rna.SUBSCRIPT)
        while len(self.path_keys) < count:
            self.path_keys.add()
        while len(self.path_keys) > count:
            self.path_keys.remove(len(self.path_keys) - 1)

    def path_input_specs(self):
        """The Data input (only used when the path starts at it) and one
        input per `[]` key."""
        specs = [
            rna.blend_data_spec(
                "data", "Data", self.path_input_type, hide=self.path_root != "INPUT"
            )
        ]
        parts = self.path_parts() or []
        steps = rna.resolve(self.path_root_step(), parts)
        key = 0
        for part, step in zip(parts, steps):
            if part != rna.SUBSCRIPT:
                continue
            mode = self.path_keys[key].mode if key < len(self.path_keys) else "INDEX"
            label = rna.label(step)
            if mode == "INDEX":
                specs.append(Integer(f"key_{key}", label))
            elif mode == "NAME":
                specs.append(String(f"key_{key}", label))
            key += 1
        return specs

    # -- pasting ---------------------------------------------------------------

    def paste_path(self, text, context=None):
        """Set the path from a copied Python path. Raises ValueError."""
        parsed = rna.parse(text)
        if context is not None:
            parsed = rna.prefer_context(parsed, context)
        self.path_root = parsed.root
        self.path_input_type = parsed.input_type
        self.path_cast = ""
        self.path = rna.join(parsed.segments)
        self._fit_path_keys()
        for entry, value in zip(self.path_keys, parsed.keys):
            entry.mode = "INDEX" if isinstance(value, int) else "NAME"
        self.sync_sockets()
        for i, value in enumerate(parsed.keys):
            socket = self.socket(f"key_{i}")
            if socket is not None:
                socket.value = value

    # -- UI --------------------------------------------------------------------

    def path_label(self):
        """ "Render › FPS" for the node header."""
        steps = self.path_steps()
        labels = []
        for step in steps:
            if step.is_subscript and labels:
                labels[-1] += "[]"
            else:
                labels.append(rna.label(step))
        return " › ".join(labels[-2:])

    def draw_path(self, layout, header=None):
        """The path editor. `header(row)` adds buttons to its first row."""
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(self, "path_root", text="", icon_only=True)
        row.prop(self, "path", text="", icon="VIEWZOOM")
        op = row.operator("sna.paste_blender_path", text="", icon="PASTEDOWN")
        op.node_id = self.id
        if header is not None:
            header(row)

        if self.path_root == "INPUT" and not linked_rna_type(self.socket("data"))[0]:
            col.prop(self, "path_input_type", text="", icon="RNA")

        parts = self.path_parts()
        if parts is None:
            col.label(text="Invalid path", icon="ERROR")
            return
        owner = self.path_root_step()
        key = 0
        for part, step in zip(parts, rna.resolve(owner, parts)):
            if part == rna.SUBSCRIPT and key < len(self.path_keys):
                row = col.row(align=True)
                row.label(text=rna.label(owner))
                row.prop(self.path_keys[key], "mode", expand=True)
                key += 1
            elif owner.known and owner.rna_type and not step.known:
                col.label(text=f"{rna.label(owner)} has no '{part}'", icon="QUESTION")
            owner = step

        final = self.path_final(cast=False)
        if final.rna_type and rna.subtypes(final.rna_type):
            col.prop(self, "path_cast", icon="RNA")
