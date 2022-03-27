import bpy
from ..base_node import SN_ScriptingBaseNode
from ...settings.data_properties import bpy_to_indexed_sections, bpy_to_path_sections



def segment_is_indexable(segment):
    """ Returns if a segment can be indexed. A segment is a string part of a data path """
    return "[" in segment and "]" in segment
    
def data_path_from_inputs(inputs, data):
    """ Returns the data path based on the given inputs and data """
    data_path = ""

    inp_index = 0
    for segment in data:
        if data_path and not segment[0] == "[":
            data_path += f".{segment.split('[')[0]}"
        else:
            data_path += f"{segment.split('[')[0]}"
        
        if segment_is_indexable(segment):
            if inputs[inp_index].bl_label == "Property":
                data_path = inputs[inp_index].python_value
            else:
                data_path += f"[{inputs[inp_index].python_value}]"
            inp_index += 1
    return data_path

class SN_BlenderPropertyNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BlenderPropertyNode"
    bl_label = "Blender Property"
    node_color = "PROPERTY"
            
    def _is_valid_data_path(self, path):
        return path and "bpy." in path and not ".ops." in path

    def get_data(self):
        if self._is_valid_data_path(self.pasted_data_path):
            sections = bpy_to_path_sections(self.pasted_data_path, True)
            if "bpy." in self.pasted_data_path: sections.insert(0, "bpy")
            return sections
        return None
    
    
    def create_inputs_from_path(self):
        """ Creates the inputs for the given data path """
        self.inputs.clear()
        data = self.get_data()
        if data:
            for segment in data:
                if segment_is_indexable(segment):
                    name = segment.split("[")[0].replace("_", " ").title()
                    if '"' in segment or "'" in segment:
                        inp = self.add_string_input(name)
                        inp["default_value"] = segment.split("[")[-1].split("]")[0][1:-1]
                        inp.index_type = "String"
                    else:
                        inp = self.add_integer_input(name)
                        inp["default_value"] = int(segment.split("[")[-1].split("]")[0])
                        inp.index_type = "Integer"
                    inp.indexable = True
        
        
    def get_pasted_prop_name(self):
        if self.pasted_data_path:
            data = self.get_data()
            if data[-1][0] == "[":
                return data[-1]
            return data[-1].replace("_", " ").title()
        return "Property"
    
    def on_prop_change(self, context):
        name = self.get_pasted_prop_name()
        self.label = name
        self.outputs[0].name = name 
        self.outputs[0].set_hide(self.pasted_data_path == "")
        self.outputs[1].set_hide(self.pasted_data_path == "")
        self.create_inputs_from_path()
        self._evaluate(context)
        
    pasted_data_path: bpy.props.StringProperty(name="Pasted Path",
                                description="The full data path to the property",
                                update=on_prop_change)
    

    def on_create(self, context):
        self.add_property_output("Property").set_hide(True)
        out = self.add_data_output("Value")
        out.changeable = True
        out.set_hide(True)
        

    def evaluate(self, context):
        if not self.pasted_data_path:
            self.outputs[0].reset_value()
        else:
            data = self.get_data()
            data_path = data_path_from_inputs(self.inputs, data)
            
            self.outputs[0].python_value = data_path
            self.outputs[1].python_value = data_path


    def draw_node(self, context, layout):
        row = layout.row(align=True)
        row.scale_y = 1.2
        op = row.operator("sn.paste_data_path", text=self.get_pasted_prop_name() if self.pasted_data_path else "Paste Property", icon="PASTEDOWN")
        op.node = self.name
        op.node_tree = self.node_tree.name
        if self.pasted_data_path:
            op = row.operator("sn.reset_data_path", text="", icon="LOOP_BACK")
            op.node = self.name
            op.node_tree = self.node_tree.name
            
    def draw_node_panel(self, context, layout):
        layout.prop(self, "pasted_data_path", text="Data Path")