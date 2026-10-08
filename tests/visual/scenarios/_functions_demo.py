"""A small add-on built from functions (node groups), shared by the
functions scenarios:

    Double(Value) -> Result                  pure function
    Greet(Run, Name) -> (Next, Greeting)     flow function, prints and returns
    Header(Layout) -> Next                   draws UI

The Main tree has an operator calling Greet and a 3D viewport panel drawn
partly by Header, with a label showing Double(21) and a button running the
operator.
"""

import bpy
import helpers

FLOW = "ScriptingFlowSocket"
FLOAT = "ScriptingFloatSocket"
STRING = "ScriptingStringSocket"


def ref(node):
    return helpers.sn("src.core.references").display_name(node)


def build():
    bpy.context.scene.sna.addon.addon_name = "Functions Demo"

    double, d_in, d_out = helpers.new_function(
        "Double", inputs=[("Value", FLOAT)], outputs=[("Result", FLOAT)]
    )
    math = helpers.add_node(double, "SNA_Node_Math", (0, 0))
    math.operation = "MULTIPLY"
    math.inputs["b"].value = 2
    helpers.link(double, d_in.outputs[0], math.inputs["a"])
    helpers.link(double, math.outputs["result"], d_out.inputs[0])

    greet, g_in, g_out = helpers.new_function(
        "Greet",
        inputs=[("Run", FLOW), ("Name", STRING)],
        outputs=[("Next", FLOW), ("Greeting", STRING)],
    )
    g_in.location = (-450, 0)
    g_out.location = (450, 0)
    combine = helpers.add_node(greet, "SNA_Node_CombineStrings", (-180, -150))
    combine.inputs["first"].value = "Hello, "
    helpers.link(greet, g_in.outputs[1], combine.socket("string"))
    say = helpers.add_node(greet, "SNA_Node_Print", (120, 80))
    helpers.link(greet, g_in.outputs[0], say.inputs[0])
    helpers.link(greet, combine.outputs[0], say.inputs["text"])
    helpers.link(greet, say.outputs[0], g_out.inputs[0])
    helpers.link(greet, combine.outputs[0], g_out.inputs[1])

    header, h_in, h_out = helpers.new_function(
        "Header", inputs=[("Layout", FLOW)], outputs=[("Next", FLOW)]
    )
    for item in header.interface.items_tree:
        item.kind = "INTERFACE"
    helpers.flush()
    title = helpers.add_node(header, "SNA_Node_Label", (0, 0))
    title.inputs["text"].value = "Drawn by the Header function"
    helpers.link(header, h_in.outputs[0], title.inputs[0])
    helpers.link(header, title.outputs[0], h_out.inputs[0])

    tree = helpers.new_tree("Main")
    operator = helpers.add_node(tree, "SNA_Node_Operator", (-700, 300))
    operator.inputs["label"].value = "Say Hello"
    call_greet = helpers.call_function(tree, greet, (-350, 300))
    call_greet.inputs["Name"].value = "World"
    shout = helpers.add_node(tree, "SNA_Node_Print", (-50, 300))
    helpers.link(tree, operator.outputs["execute"], call_greet.inputs[0])
    helpers.link(tree, call_greet.outputs[0], shout.inputs[0])
    helpers.link(tree, call_greet.outputs[1], shout.inputs["text"])

    panel = helpers.add_node(tree, "SNA_Node_Panel", (-700, -100))
    panel.inputs["label"].value = "Functions Demo"
    call_header = helpers.call_function(tree, header, (-400, -100))
    call_double = helpers.call_function(tree, double, (-400, -350))
    call_double.inputs["Value"].value = 21
    text = helpers.add_node(tree, "SNA_Node_CombineStrings", (-150, -300))
    text.inputs["first"].value = "Double(21) = "
    label = helpers.add_node(tree, "SNA_Node_Label", (100, -100))
    button = helpers.add_node(tree, "SNA_Node_Button", (350, -100))
    helpers.link(tree, panel.outputs["body"], call_header.inputs[0])
    helpers.link(tree, call_header.outputs[0], label.inputs[0])
    helpers.link(tree, call_double.outputs[0], text.socket("string"))
    helpers.link(tree, text.outputs[0], label.inputs["text"])
    helpers.link(tree, label.outputs[0], button.inputs[0])
    helpers.flush()
    button.operator_sn = ref(operator)
    button.inputs["label"].value = "Say Hello"
    helpers.flush()
    return tree, {"Double": double, "Greet": greet, "Header": header}
