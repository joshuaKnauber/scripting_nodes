import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_AreaLocationsNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_AreaLocationsNode"
    bl_label = "Area Locations"
    node_color = "DEFAULT"

    def on_create(self, context):
        self.add_property_input("Area")
        self.add_integer_vector_output("Top Left").size = 2
        self.add_integer_vector_output("Top Center").size = 2
        self.add_integer_vector_output("Top Right").size = 2
        self.add_integer_vector_output("Bottom Left").size = 2
        self.add_integer_vector_output("Bottom Center").size = 2
        self.add_integer_vector_output("Bottom Right").size = 2
        self.add_integer_vector_output("Left Center").size = 2
        self.add_integer_vector_output("Right Center").size = 2
        self.add_integer_vector_output("Center").size = 2
        
    def evaluate(self, context):
        self.code_imperative = """
            def region_by_type(area, region_type):
                for region in area.regions:
                    if region.type == region_type:
                        return region
                return area.regions[0]
        """
        
        self.outputs["Top Left"].python_value = f"(0, region_by_type({self.inputs['Area'].python_value}, 'WINDOW').height)"
        self.outputs["Top Center"].python_value = f"(region_by_type({self.inputs['Area'].python_value}, 'WINDOW').width/2, region_by_type({self.inputs['Area'].python_value}, 'WINDOW').height)"
        self.outputs["Top Right"].python_value = f"(region_by_type({self.inputs['Area'].python_value}, 'WINDOW').width, region_by_type({self.inputs['Area'].python_value}, 'WINDOW').height)"
        self.outputs["Bottom Left"].python_value = f"(0, 0)"
        self.outputs["Bottom Center"].python_value = f"(region_by_type({self.inputs['Area'].python_value}, 'WINDOW').width/2, 0)"
        self.outputs["Bottom Right"].python_value = f"(region_by_type({self.inputs['Area'].python_value}, 'WINDOW').width, 0)"
        self.outputs["Left Center"].python_value = f"(0, region_by_type({self.inputs['Area'].python_value}, 'WINDOW').height/2)"
        self.outputs["Right Center"].python_value = f"(region_by_type({self.inputs['Area'].python_value}, 'WINDOW').width, region_by_type({self.inputs['Area'].python_value}, 'WINDOW').height/2)"
        self.outputs["Center"].python_value = f"(region_by_type({self.inputs['Area'].python_value}, 'WINDOW').width/2, region_by_type({self.inputs['Area'].python_value}, 'WINDOW').height/2)"