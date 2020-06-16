import bpy

class ScriptingNodesProperties(bpy.types.PropertyGroup):

    def update_auto_compile(self,context):
        """ function for updating the auto compile property """

    # if true the node tree gets recompiled on changes
    auto_compile: bpy.props.BoolProperty(default=False, name="Auto Reload", description="Automatically reloads the addon when changes are made", update=update_auto_compile)

    # show the line width property in the ui
    show_line_width: bpy.props.BoolProperty(default=False,name="Show settings",description="Show settings for the error panel")

    # the width of a line in the errors panel
    line_width: bpy.props.IntProperty(default=10,min=1,max=50,name="Error line breaks",description="How often the error message lines should break to the next line")

    # this is true when a package has been installed and blender hasn't been restarted yet
    package_installed_without_reload: bpy.props.BoolProperty(default=False)

    # this is true when a package has been uninstalled and blender hasn't been restarted yet
    package_uninstalled_without_reload: bpy.props.BoolProperty(default=False)