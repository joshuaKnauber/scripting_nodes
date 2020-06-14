import bpy
from ...compile.compiler import compiler
from random import randint


class ScriptingNodesTree(bpy.types.NodeTree):
    '''Scripting Nodes node tree'''
    bl_idname = 'ScriptingNodesTree'
    bl_label = "Scripting Nodes"
    bl_icon = 'SCRIPT'

    def update_info(self,context):
        """ compiles the addon when the addon properties are changed """
        compiler().autocompile_active()

    def get_file_name(self):
        if self.addon_name:
            return self.addon_name.lower().replace(" ","_") + ".py"
        else:
            return "sn_addon_" + str(randint(1000, 99999)) + ".py"

    # properties regarding the created addon
    addon_name: bpy.props.StringProperty(default="New Addon",name="Name",description="Name of your addon",update=update_info)
    addon_author: bpy.props.StringProperty(default="",name="Author",description="Your name",update=update_info)
    addon_description: bpy.props.StringProperty(default="",name="Description",description="Description of what your addon does",update=update_info)
    addon_location: bpy.props.StringProperty(default="",name="Location",description="Location of your addon in blender",update=update_info)
    addon_wiki: bpy.props.StringProperty(default="",name="Wiki",description="Link to the documentation of your addon",update=update_info)
    addon_warning: bpy.props.StringProperty(default="",name="Warning",description="Warning message for your addon",update=update_info)
    addon_category: bpy.props.StringProperty(default="General",name="Category",description="Category of your addon",update=update_info)
    addon_blender: bpy.props.IntVectorProperty(default=bpy.app.version,min=0,name="Version",description="Required blender version for your addon",update=update_info)
    addon_version: bpy.props.IntVectorProperty(default=(1, 0, 0),min=0,name="Version",description="Version of your addon",update=update_info)

    # if true, the addon is loaded when the file is opened
    compile_on_start: bpy.props.BoolProperty(default=True,name="Reload on start",description="Reload this node tree when this file is opened")
