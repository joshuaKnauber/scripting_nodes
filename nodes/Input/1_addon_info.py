import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_AddonInfoNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_AddonInfoNode"
    bl_label = "Addon Info"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_string_output("Name")
        self.add_string_output("Description")
        self.add_string_output("Author")
        self.add_string_output("Location")
        self.add_string_output("Warning")
        self.add_string_output("Wiki URL")
        self.add_string_output("Tracker URL")
        self.add_string_output("Category")
        self.add_integer_output("Version").subtype = "VECTOR3"
        self.add_integer_output("Blender Version").subtype = "VECTOR3"


    def code_evaluate(self, context, touched_socket):
        keys = {
            "Name": "name",
            "Description": "description",
            "Author": "author",
            "Location": "location",
            "Warning": "warning",
            "Wiki URL": "wiki_url",
            "Tracker URL": "tracker_url",
            "Category": "category",
            "Version": "version",
            "Blender Version": "blender"
        }
        
        return {
            "code": f"""bl_info["{ keys[touched_socket.get_text()] }"]"""
        }