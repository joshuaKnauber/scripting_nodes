import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_BMeshVertexDataNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_BMeshVertexDataNode"
    bl_label = "BMesh Vertex Data"
    node_color = "PROPERTY"

    def update_with_transforms(self, context):
        self.inputs["Object"].set_hide(not self.with_transforms)
        self._evaluate(context)

    def on_create(self, context):
        self.add_property_input("BMesh Vertex")
        self.add_property_input("Object").set_hide(True)
        self.add_float_vector_output("Location")
        self.add_float_vector_output("Normal")
        self.add_boolean_output("Selected")
        self.add_boolean_output("Hidden")
        self.add_integer_output("Index")
        self.add_boolean_output("Is Boundary")
        self.add_boolean_output("Is Manifold")
        self.add_boolean_output("Is Wire")
        
    def evaluate(self, context):
        if self.inputs["BMesh Vertex"].is_linked:
            self.outputs["Location"].python_value = f"{self.inputs['BMesh Vertex'].python_value}.co"
            self.outputs["Normal"].python_value = f"{self.inputs['BMesh Vertex'].python_value}.normal"
            self.outputs["Selected"].python_value = f"{self.inputs['BMesh Vertex'].python_value}.select"
            self.outputs["Hidden"].python_value = f"{self.inputs['BMesh Vertex'].python_value}.hide"
            self.outputs["Index"].python_value = f"{self.inputs['BMesh Vertex'].python_value}.index"
            self.outputs["Is Boundary"].python_value = f"{self.inputs['BMesh Vertex'].python_value}.is_boundary"
            self.outputs["Is Manifold"].python_value = f"{self.inputs['BMesh Vertex'].python_value}.is_manifold"
            self.outputs["Is Wire"].python_value = f"{self.inputs['BMesh Vertex'].python_value}.is_wire"
        else:
            self.outputs["Location"].reset_value()
            self.outputs["Normal"].reset_value()
            self.outputs["Index"].reset_value()
            self.outputs["Selected"].reset_value()
            self.outputs["Hidden"].reset_value()
            self.outputs["Index"].reset_value()
            self.outputs["Is Boundary"].reset_value()
            self.outputs["Is Manifold"].reset_value()
            self.outputs["Is Wire"].reset_value()