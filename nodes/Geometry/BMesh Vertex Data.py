import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_BMeshVertexDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BMeshVertexDataNode"
    bl_label = "BMesh Vertex Data"
    node_color = "PROPERTY"

    def update_with_transforms(self, context):
        self.inputs["Object"].set_hide(not self.with_transforms)
        self._evaluate(context)

    with_transforms: bpy.props.BoolProperty(name="With Transforms", default=False, description="Apply the transforms of the input object", update=update_with_transforms)

    def on_create(self, context):
        self.add_property_input("BMesh Vertex")
        self.add_property_input("Object").set_hide(True)
        self.add_float_vector_output("Location")
        self.add_float_vector_output("Normal")
        self.add_boolean_output("Selected")
        self.add_boolean_output("Hidden")
        self.add_integer_output("Index")

    def draw_node(self, context, layout):
        layout.prop(self, "with_transforms")
        
    def evaluate(self, context):
        if self.inputs["BMesh Vertex"].is_linked:
            if self.with_transforms:
                self.outputs["Location"].python_value = f"({self.inputs['Object'].python_value}.matrix_world @ {self.inputs['BMesh Vertex'].python_value}.co).to_tuple()"
            else:
                self.outputs["Location"].python_value = f"{self.inputs['BMesh Vertex'].python_value}.co"
            self.outputs["Normal"].python_value = f"{self.inputs['BMesh Vertex'].python_value}.normal"
            self.outputs["Selected"].python_value = f"{self.inputs['BMesh Vertex'].python_value}.select"
            self.outputs["Hidden"].python_value = f"{self.inputs['BMesh Vertex'].python_value}.hide"
            self.outputs["Index"].python_value = f"{self.inputs['BMesh Vertex'].python_value}.index"
        else:
            self.outputs["Location"].reset_value()
            self.outputs["Normal"].reset_value()
            self.outputs["Index"].reset_value()
            self.outputs["Selected"].reset_value()
            self.outputs["Hidden"].reset_value()
            self.outputs["Index"].reset_value()