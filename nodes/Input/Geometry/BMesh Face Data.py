import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_BMeshFaceDataNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_BMeshFaceDataNode"
    bl_label = "BMesh Face Data"
    node_color = "PROPERTY"

    def on_create(self, context):
        self.add_property_input("BMesh Face")
        self.add_property_input("Object").set_hide(True)
        self.add_collection_property_output("Edges")
        self.add_collection_property_output("Vertices")
        self.add_float_vector_output("Center")
        self.add_float_vector_output("Center Weighted")
        self.add_float_vector_output("Normal")
        self.add_boolean_output("Selected")
        self.add_boolean_output("Hidden")
        self.add_boolean_output("Smooth")
        self.add_integer_output("Index")
        self.add_integer_output("Material Index")

    def evaluate(self, context):
        if self.inputs["BMesh Face"].is_linked:
            self.outputs["Edges"].python_value = f"{self.inputs['BMesh Face'].python_value}.edges"
            self.outputs["Vertices"].python_value = f"{self.inputs['BMesh Face'].python_value}.verts"
            self.outputs["Center"].python_value = f"{self.inputs['BMesh Face'].python_value}.calc_center_median()"
            self.outputs["Center Weighted"].python_value = f"{self.inputs['BMesh Face'].python_value}.calc_center_median_weighted()"
            self.outputs["Normal"].python_value = f"{self.inputs['BMesh Face'].python_value}.normal"
            self.outputs["Selected"].python_value = f"{self.inputs['BMesh Face'].python_value}.select"
            self.outputs["Hidden"].python_value = f"{self.inputs['BMesh Face'].python_value}.hide"
            self.outputs["Smooth"].python_value = f"{self.inputs['BMesh Face'].python_value}.smooth"
            self.outputs["Index"].python_value = f"{self.inputs['BMesh Face'].python_value}.index"
            self.outputs["Material Index"].python_value = f"{self.inputs['BMesh Face'].python_value}.material_index"
        else:
            self.outputs["Normal"].reset_value()
            self.outputs["Index"].reset_value()
            self.outputs["Selected"].reset_value()
            self.outputs["Hidden"].reset_value()
            self.outputs["Center"].reset_value()
            self.outputs["Center Weighted"].reset_value()
            self.outputs["Smooth"].reset_value()
            self.outputs["Edges"].reset_value()
            self.outputs["Vertices"].reset_value()
            self.outputs["Material Index"].reset_value()