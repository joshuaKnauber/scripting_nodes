import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_BMeshEdgeDataNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_BMeshEdgeDataNode"
    bl_label = "BMesh Edge Data"
    node_color = "PROPERTY"

    def update_with_transforms(self, context):
        self.inputs["Object"].set_hide(not self.with_transforms)
        self._evaluate(context)

    def on_create(self, context):
        self.add_property_input("BMesh Edge")
        self.add_property_input("Object").set_hide(True)
        self.add_collection_property_output("Vertices")
        self.add_collection_property_output("Faces")
        self.add_boolean_output("Selected")
        self.add_boolean_output("Hidden")
        self.add_boolean_output("Smooth")
        self.add_integer_output("Index")
        self.add_boolean_output("Is Manifold")
        self.add_boolean_output("Is Boundary")
        self.add_boolean_output("Is Contiguous")
        self.add_boolean_output("Is Convex")
        self.add_boolean_output("Is Wire")
        self.add_boolean_output("Is Seam")

    def evaluate(self, context):
        if self.inputs["BMesh Edge"].is_linked:
            self.outputs["Faces"].python_value = f"{self.inputs['BMesh Edge'].python_value}.link_faces"
            self.outputs["Vertices"].python_value = f"{self.inputs['BMesh Edge'].python_value}.verts"
            self.outputs["Is Boundary"].python_value = f"{self.inputs['BMesh Edge'].python_value}.is_boundary"
            self.outputs["Is Contiguous"].python_value = f"{self.inputs['BMesh Edge'].python_value}.is_contiguous"
            self.outputs["Is Convex"].python_value = f"{self.inputs['BMesh Edge'].python_value}.is_convex"
            self.outputs["Is Wire"].python_value = f"{self.inputs['BMesh Edge'].python_value}.is_wire"
            self.outputs["Is Seam"].python_value = f"{self.inputs['BMesh Edge'].python_value}.seam"
            self.outputs["Selected"].python_value = f"{self.inputs['BMesh Edge'].python_value}.select"
            self.outputs["Hidden"].python_value = f"{self.inputs['BMesh Edge'].python_value}.hide"
            self.outputs["Smooth"].python_value = f"{self.inputs['BMesh Edge'].python_value}.smooth"
            self.outputs["Index"].python_value = f"{self.inputs['BMesh Edge'].python_value}.index"
            self.outputs["Is Manifold"].python_value = f"{self.inputs['BMesh Edge'].python_value}.is_manifold"
        else:
            self.outputs["Index"].reset_value()
            self.outputs["Selected"].reset_value()
            self.outputs["Hidden"].reset_value()
            self.outputs["Smooth"].reset_value()
            self.outputs["Is Boundary"].reset_value()
            self.outputs["Is Contiguous"].reset_value()
            self.outputs["Is Convex"].reset_value()
            self.outputs["Is Wire"].reset_value()
            self.outputs["Is Seam"].reset_value()
            self.outputs["Vertices"].reset_value()
            self.outputs["Faces"].reset_value()
            self.outputs["Is Manifold"].reset_value()