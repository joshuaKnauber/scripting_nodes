import bpy
from ..base_node import SN_ScriptingBaseNode


"""
this design is still missing the option to put in other data blocks.
for example for getting the name of an object, you may want to put in the active object

we still need a way to get blend data on blend data that you cant copy
"""



class SN_GetDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetDataNode"
    bl_label = "Get Data"

    def on_create(self, context):
        self.add_data_output("Data")
        
        
    def update_data_type(self, context):
        self.convert_socket(self.outputs[0], self.socket_names[self.data_type])
        self._evaluate(context)

    data_type: bpy.props.EnumProperty(name="Type",
                                    description="The type of data of this property",
                                    items=[("Data", "Data", "Data"),
                                           ("String", "String", "String"),
                                            ("Enum", "Enum", "Enum"),
                                            ("Boolean", "Boolean", "Boolean"),
                                            ("Float", "Float", "Float")],
                                    update=update_data_type)


    def disect_data_path(self, path):
        # remove assign part
        path = path.split("=")[0]
        path = path.strip()
        # replace escaped quotes
        path = path.replace('\\"', '"')
        # split data path in segments
        segments = path.split(".")[1:]
        # remove indexing from property name
        segments[-1] = segments[-1].split("[")[0]
        return segments

    def is_valid_data_path(self, path):
        return path and "bpy." in path and not ".ops." in path

    def get_data(self):
        if self.is_valid_data_path(self.data_path):
            return self.disect_data_path(self.data_path)
        return None
    
    def segment_is_indexable(self, segment):
        """ Returns if a segment can be indexed. A segment is a string part of a data path """
        return "[" in segment and "]" in segment
    
    def create_inputs_from_path(self, path):
        """ Creates the inputs for the given data path """
        for segment in path:
            if self.segment_is_indexable(segment):
                if '"' in segment or "'" in segment:
                    inp = self.add_string_input(segment.split("[")[0].replace("_", " ").title())
                    inp["default_value"] = segment.split("[")[-1].split("]")[0][1:-1]
                    inp.index_type = "String"
                else:
                    inp = self.add_integer_input(segment.split("[")[0].replace("_", " ").title())
                    inp["default_value"] = int(segment.split("[")[-1].split("]")[0])
                    inp.index_type = "Integer"
                inp.indexable = True

    def update_output_from_path(self, context, path):
        """ Updates the outputs name and type from the given data path """
        self.outputs[0].name = path[-1].replace("_", " ").title()
        if context.scene.sn.last_copied_datapath == self.data_path:
            # TODO remove this when all data types are supported
            if context.scene.sn.last_copied_datatype in self.socket_names:
                self.data_type = context.scene.sn.last_copied_datatype  

    def update_data_path(self, context):
        """ Update the inputs of this node to reflect the new data path """
        self.inputs.clear()
        path = self.get_data()
        if path:
            self.create_inputs_from_path(path)              
            self.update_output_from_path(context, path)
        self._evaluate(context)

    data_path: bpy.props.StringProperty(update=update_data_path,
                                        name="Data Path",
                                        description="Path of the property to return")
    
    def evaluate(self, context):
        path = self.get_data()
        if path:
            value = "bpy."
            index_segment = 0
            for segment in self.get_data():
                if self.segment_is_indexable(segment):
                    # TODO remove rest if blend data
                    value += segment.split("[")[0] + "[" + self.inputs[index_segment].python_value + "]."
                    index_segment += 1
                else:
                    value += segment + "."
            self.outputs[0].python_value = value[:-1]
        else:
            self.outputs[0].reset_value()

    def draw_node(self, context, layout):
        layout.prop(self, "data_type")
        row = layout.row()
        row.scale_y = 1.25
        op = row.operator("sn.paste_data_path", text="Paste Property", icon="PASTEDOWN")
        op.node_tree = self.node_tree.name
        op.node = self.name

    def draw_node_panel(self, context, layout):
        layout.prop(self, "data_path")
        layout.label(text=str(self.get_data()))