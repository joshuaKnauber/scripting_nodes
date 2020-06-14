import bpy

class ScriptingNodesProperties(bpy.types.PropertyGroup):

    def update_auto_compile(self,context):
        """ function for updating the auto compile property """

    # if true the node tree gets recompiled on changes
    auto_compile: bpy.props.BoolProperty(default=False, name="Auto Reload", description="Automatically reloads the addon when changes are made", update=update_auto_compile)