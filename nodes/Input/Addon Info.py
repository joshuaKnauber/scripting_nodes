import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_AddonInfoNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_AddonInfoNode"
    bl_label = "Addon Info"
    node_color = "DEFAULT"

    def on_create(self, context):
        self.add_string_output("Name")
        self.add_string_output("Description")
        self.add_string_output("Author")
        self.add_string_output("Location")
        self.add_string_output("Warning")
        self.add_string_output("Doc URL")
        self.add_string_output("Tracker URL")
        self.add_string_output("Category")
        self.add_integer_vector_output("Version")
        self.add_integer_vector_output("Blender Version")

    def evaluate(self, context):
        self.outputs[0].python_value = f"bpy.context.scene.sn.addon_name"
        self.outputs[1].python_value = f"bpy.context.scene.sn.description"
        self.outputs[2].python_value = f"bpy.context.scene.sn.author"
        self.outputs[3].python_value = f"bpy.context.scene.sn.location"
        self.outputs[4].python_value = f"bpy.context.scene.sn.warning"
        self.outputs[5].python_value = f"bpy.context.scene.sn.doc_url"
        self.outputs[6].python_value = f"bpy.context.scene.sn.tracker_url"
        self.outputs[7].python_value = f"bpy.context.scene.sn.category"
        self.outputs[8].python_value = f"tuple(bpy.context.scene.sn.version)"
        self.outputs[9].python_value = f"tuple(bpy.context.scene.sn.blender)"

    def evaluate_export(self, context):
        self.outputs[0].python_value = bpy.context.scene.sn.addon_name
        self.outputs[1].python_value = bpy.context.scene.sn.description
        self.outputs[2].python_value = bpy.context.scene.sn.author
        self.outputs[3].python_value = bpy.context.scene.sn.location
        self.outputs[4].python_value = bpy.context.scene.sn.warning
        self.outputs[5].python_value = bpy.context.scene.sn.doc_url
        self.outputs[6].python_value = bpy.context.scene.sn.tracker_url
        self.outputs[7].python_value = bpy.context.scene.sn.category
        self.outputs[8].python_value = tuple(bpy.context.scene.sn.version)
        self.outputs[9].python_value = tuple(bpy.context.scene.sn.blender)