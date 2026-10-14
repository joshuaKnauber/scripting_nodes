"""Text for nodes that draw it: the String input, or a Text data-block for
text over several lines (edited in the Text Editor).

    class SNA_Node_Markdown(TextSourceMixin, ScriptingBaseNode, bpy.types.Node):
        def socket_specs(self):
            return [Interface(), self.text_input_spec()], [Interface("next")]

        def emit(self, ctx):
            text = self.text_expression(ctx)

Also watches the sources of nodes that have a `source_fingerprint()` (these
nodes, Script nodes): editing a text or saving a file triggers no RNA update.
"""

import bpy

from ..core import scheduler
from ..lib.trees import scripting_node_trees
from ..sockets.spec import String


class TextSourceMixin:
    text_block: bpy.props.PointerProperty(
        type=bpy.types.Text,
        name="Text",
        description="Use the contents of a text data-block (for several lines)",
    )

    def text_input_spec(self):
        """The String input, removed while a text data-block is picked."""
        return String("text", "Text", enabled=self.text_block is None)

    def text_expression(self, ctx):
        if self.text_block is not None:
            return repr(self.text_block.as_string())
        return ctx.input("text")

    def source_fingerprint(self):
        return hash(self.text_block.as_string()) if self.text_block else None

    def draw_text_block(self, layout):
        layout.template_ID(self, "text_block", new="text.new", open="text.open")


# node id -> last seen source fingerprint
_fingerprints = {}


def _watch_sources():
    seen = set()
    for tree in scripting_node_trees():
        for node in tree.nodes:
            fingerprint = getattr(node, "source_fingerprint", None)
            if fingerprint is None:
                continue
            seen.add(node.id)
            value = fingerprint()
            if node.id in _fingerprints and _fingerprints[node.id] != value:
                node.mark_dirty()
            _fingerprints[node.id] = value
    for node_id in set(_fingerprints) - seen:
        del _fingerprints[node_id]


def register():
    scheduler.add_watcher(_watch_sources)


def unregister():
    scheduler.remove_watcher(_watch_sources)
    _fingerprints.clear()
