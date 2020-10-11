import bpy



def add_basic_nodes(tree):
    """ adds the basic nodes when adding a new node tree """
    panel = tree.nodes.new("SN_PanelNode")
    button = tree.nodes.new("SN_ButtonNode")
    run_operator = tree.nodes.new("SN_RunOperator")
    operator = tree.nodes.new("SN_CreateOperator")
    print_ = tree.nodes.new("SN_PrintNode")
    string = tree.nodes.new("SN_StringNode")
    frame_ops = tree.nodes.new("NodeFrame")
    frame_layout = tree.nodes.new("NodeFrame")

    button.inputs[1].set_value("I print in the Visual Scripting N-Panel!")
    button.icon = "OUTPUT"
    run_operator.search_prop = "custom"
    run_operator.propName = "My Operator"
    string.string_value = "Test Print"
    frame_ops.label = "Operator"
    frame_layout.label = "Layout / UI"
    frame_ops.use_custom_color = True
    frame_ops.color = (0.3,0.3,0.3)
    frame_layout.use_custom_color = True
    frame_layout.color = (0.6,0.6,0.6)

    tree.links.new(panel.outputs[1],button.inputs[0])
    tree.links.new(button.outputs[0],run_operator.inputs[0])
    tree.links.new(operator.outputs[0],print_.inputs[0])
    tree.links.new(string.outputs[0],print_.inputs[1])

    operator.location = (-150,300)
    print_.location = (150,300)
    string.location = (150,150)
    panel.location = (-150,0)
    button.location = (150,0)
    run_operator.location = (350,0)

    panel.parent = frame_layout
    button.parent = frame_layout
    run_operator.parent = frame_layout
    operator.parent = frame_ops
    print_.parent = frame_ops
    string.parent = frame_ops

    tree.use_fake_user = True
    tree.added_basic_nodes = True



def handle_depsgraph_update():
    for area in bpy.context.screen.areas:
        if area.type == "NODE_EDITOR":
            if area.spaces[0].tree_type == "ScriptingNodesTree":
                if area.spaces[0].node_tree:
                    if hasattr(area.spaces[0].node_tree,"added_basic_nodes"):
                        if not area.spaces[0].node_tree.added_basic_nodes:
                            add_basic_nodes(area.spaces[0].node_tree)

                            prefs = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences
                            if not prefs.has_seen_tutorial:
                                bpy.ops.scripting_nodes.welcome_message("INVOKE_DEFAULT")

    if ".sn_primer" in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[".sn_primer"])