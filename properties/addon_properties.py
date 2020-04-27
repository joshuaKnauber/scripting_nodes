import bpy


class ScriptingNodesProperties(bpy.types.PropertyGroup):

    auto_compile: bpy.props.BoolProperty(default=False,name="Auto Reload",description="Automatically reload the node tree on change")



bpy.utils.register_class(ScriptingNodesProperties)
bpy.types.Scene.sn_properties = bpy.props.PointerProperty(type=ScriptingNodesProperties)
