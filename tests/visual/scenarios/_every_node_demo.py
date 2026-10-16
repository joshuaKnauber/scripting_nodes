"""An add-on using every node, each in its own tree with defaults: what the
generated code looks like for nodes the Object Toolkit doesn't use.
`python scripts/example_addon.py every_node` builds and exports it.

    Program nodes   Operator -> node -> Print of each output
    Interface nodes Panel -> node -> Label
    Value nodes     Operator -> Print of each output
    Root nodes      on their own (operators, panels, events, ...)

Nodes that need more setup (pick a property, an operator, ...) show an
error and write no code; the trees are kept anyway.
"""

import bpy
import helpers

FLOW = "ScriptingFlowSocket"
SKIP = {
    "SNA_Node_Trigger",  # left out of exports
    "SNA_Node_Group",  # needs a function
}


def first_flow(sockets, kinds):
    for socket in sockets:
        if socket.bl_idname == FLOW and socket.kind in kinds and socket.enabled:
            return socket
    return None


def data_outputs(node):
    return [
        s
        for s in node.outputs
        if getattr(s, "socket_type", None) == "DATA" and s.enabled
    ]


def build_node(cls):
    tree = helpers.new_tree(cls.bl_label)
    node = helpers.add_node(tree, cls.bl_idname, (0, 0))
    helpers.flush()
    program_in = first_flow(node.inputs, {"PROGRAM", "LOGIC"})
    interface_in = first_flow(node.inputs, {"INTERFACE"})
    if interface_in is not None:
        panel = helpers.add_node(tree, "SNA_Node_Panel", (-300, 0))
        panel.inputs["label"].value = cls.bl_label
        helpers.link(tree, panel.outputs["body"], interface_in)
        after = first_flow(node.outputs, {"INTERFACE"})
        if after is not None:
            label = helpers.add_node(tree, "SNA_Node_Label", (300, 0))
            helpers.link(tree, after, label.inputs[0])
        return
    previous = None
    if program_in is not None:
        operator = helpers.add_node(tree, "SNA_Node_Operator", (-300, 0))
        operator.inputs["label"].value = cls.bl_label
        helpers.link(tree, operator.outputs["execute"], program_in)
        previous = first_flow(node.outputs, {"PROGRAM"})
    elif not node.sn_root and data_outputs(node):
        operator = helpers.add_node(tree, "SNA_Node_Operator", (-300, 0))
        operator.inputs["label"].value = cls.bl_label
        previous = operator.outputs["execute"]
    if previous is None:
        return
    for i, output in enumerate(data_outputs(node)):
        printer = helpers.add_node(tree, "SNA_Node_Print", (300, -150 * i))
        helpers.link(tree, previous, printer.inputs[0])
        helpers.link(tree, output, printer.socket("text"))
        previous = printer.outputs[0]


def build():
    bpy.context.scene.sna.addon.addon_name = "Every Node"
    for cls in helpers.node_classes():
        if cls.bl_idname not in SKIP:
            build_node(cls)
    helpers.flush()
