import bpy


class ScriptingNodesProperties(bpy.types.PropertyGroup):

    auto_compile: bpy.props.BoolProperty(default=False,name="Auto Reload",description="Automatically reload the node tree on change")

    examples: bpy.props.EnumProperty(
        items=[("None", "Please choose an example", "Please choose an example"),
               ("add_monkey", "Monkey adder", "Creates a button that makes a monkey"),
               ("add_monkey_size", "Monkey adder choose size", "Creates a button that makes a monkey with chooseble size")],
        name="Examples",
        description="Example Node Trees"
    )


bpy.utils.register_class(ScriptingNodesProperties)
bpy.types.Scene.sn_properties = bpy.props.PointerProperty(type=ScriptingNodesProperties)
