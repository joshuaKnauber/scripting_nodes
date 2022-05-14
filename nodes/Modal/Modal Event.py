import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_ModalEventNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ModalEventNode"
    bl_label = "Modal Event"
    node_color = "DEFAULT"

    def on_create(self, context):
        self.add_string_output("Type")
        self.add_boolean_output("Value")
        self.add_boolean_output("Alt")
        self.add_boolean_output("Shift")
        self.add_boolean_output("Ctrl")
        self.add_boolean_output("Os Key")
        self.add_integer_output("Mouse Region X")
        self.add_integer_output("Mouse Region Y")
        self.add_integer_output("Mouse X")
        self.add_integer_output("Mouse Y")
        self.add_integer_output("Mouse Offset X")
        self.add_integer_output("Mouse Offset Y")
        self.add_float_output("Pressure")
        self.add_float_output("Tilt")
        # When adding options here, also add them to the modal call where it's saved
        
    def draw_node(self, context, layout):
        for node in self.root_nodes:
            if node.bl_idname == "SN_ModalOperatorNode":
                break
        else:
            row = layout.row()
            row.alert = True
            row.label(text="This node only works with modal operators!", icon="ERROR")

    def evaluate(self, context):
        self.outputs["Type"].python_value = f"event.type"
        self.outputs["Value"].python_value = f"event.value"
        self.outputs["Alt"].python_value = f"event.alt"
        self.outputs["Shift"].python_value = f"event.shift"
        self.outputs["Ctrl"].python_value = f"event.ctrl"
        self.outputs["Os Key"].python_value = f"event.oskey"
        self.outputs["Mouse Region X"].python_value = f"event.mouse_region_x"
        self.outputs["Mouse Region Y"].python_value = f"event.mouse_region_y"
        self.outputs["Mouse X"].python_value = f"event.mouse_x"
        self.outputs["Mouse Y"].python_value = f"event.mouse_y"
        self.outputs["Mouse Offset X"].python_value = f"(event.mouse_x - self.start_pos[0])"
        self.outputs["Mouse Offset Y"].python_value = f"(event.mouse_y - self.start_pos[1])"
        self.outputs["Pressure"].python_value = f"event.pressure"
        self.outputs["Tilt"].python_value = f"event.tilt"