import bpy
import mathutils
from ..base_node import SN_ScriptingBaseNode
from ..templates.GetDataNode import GetDataNode



class SN_GetDataNode(bpy.types.Node, SN_ScriptingBaseNode, GetDataNode):

    bl_idname = "SN_GetDataNode"
    bl_label = "Get Data"
    bl_width_default = 250

    def on_create(self, context):
        self.add_data_output("Data").hide = True


    def disect_data_path(self, path):
        # remove assign part
        path = path.split("=")[0]
        path = path.strip()
        # replace escaped quotes
        path = path.replace('\\"', '"')
        # split data path in segments
        segments = []
        for segment in path.split(".")[1:]:
            if segments and "[" in segments[-1] and not "]" in segments[-1]:
                segments[-1] += f".{segment}"
            else:
                segments.append(segment)
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
    
    def create_inputs_from_path(self):
        """ Creates the inputs for the given data path """
        self.inputs.clear()
        path = self.get_data()
        if path:
            for segment in path:
                if self.segment_is_indexable(segment):
                    if '"' in segment or "'" in segment:
                        inp = self.add_string_input(segment.split("[")[0].replace("_", " ").title() + " (Indexed)")
                        inp["default_value"] = segment.split("[")[-1].split("]")[0][1:-1]
                        inp.index_type = "String"
                    else:
                        inp = self.add_integer_input(segment.split("[")[0].replace("_", " ").title() + " (Indexed)")
                        inp["default_value"] = int(segment.split("[")[-1].split("]")[0])
                        inp.index_type = "Integer"
                    inp.indexable = True
                if segment == self.return_data:
                    break


    def update_output_from_data(self):
        """ Updates the outputs name and type from the given data path """
        if self.return_data != "NONE":
            for item in self.return_data_items(bpy.context):
                if item[0] == self.return_data:
                    self.outputs[0].name = item[1]
                    break
            self.outputs[0].hide = False
        else:
            self.outputs[0].name = "Data"
            self.outputs[0].hide = True
    
    
    def get_path_to_return(self):
        """ Returns the pasted data path until the chosen segment """
        path = self.get_data()
        data_path = "bpy"
        if path:
            for segment in path:
                data_path += f".{segment}"
                if segment == self.return_data:
                    break
        return data_path
    
    
    def socket_type_by_value_type(self, value):
        types = {
            "String": str,
            "Boolean": bool,
            "Float": float,
            "Integer": int,
            "List": list,
            "Float Vector": mathutils.Vector,
            "Float Vector": mathutils.Euler,
            "Float Vector": mathutils.Color,
            "Float Vector": mathutils.Quaternion,
        }
        for name in types:
            if types[name] == type(value):
                return name
        if hasattr(value, "bl_rna"):
            return "Blend Data"
        return "Data"
    
    def guess_output_data_type(self):
        """ Tries to find the pasted data and set the data type """
        path = self.get_path_to_return()
        if path != "bpy":
            try:
                value = eval(self.get_path_to_return())
                self.data_type = self.socket_type_by_value_type(value)
            except Exception as err:
                print(err, self.get_path_to_return())
                self.data_type = "Data"
            if self.data_type == "Data":
                self.data_type_not_set = True


    def update_return_data(self, context):
        self.create_inputs_from_path()
        self.update_output_from_data()
        self.guess_output_data_type()

    def return_data_items(self, context):
        """ Returns the segments from the current data path """
        path = self.get_data()
        if path:
            items = []
            for segment in path:
                name = segment.split("[")[0].replace("_", " ").title()
                if self.segment_is_indexable(segment):
                    name = f"{name} (Indexed)"
                items.append((segment, name, segment))
            return items
        return [("NONE", "NONE", "NONE")]
    
    return_data: bpy.props.EnumProperty(name="Return Data",
                                        description="The data that this node should return",
                                        update=update_return_data,
                                        items=return_data_items)


    def update_data_path(self, context):
        """ Update the inputs of this node to reflect the new data path """
        self.return_data = self.return_data_items(context)[-1][0]
        self._evaluate(context)

    data_path: bpy.props.StringProperty(update=update_data_path,
                                        name="Data Path",
                                        description="Path of the property to return")
    
    
    def evaluate(self, context):
        path = self.get_data()
        if not path:
            self.outputs[0].reset_value()
        else:
            data_path = "bpy"

            inp_index = 0
            for i in range(len(self.inputs)):
                if self.inputs[i].indexable:
                    inp_index = i
                    break
                
            for segment in path:
                data_path += f".{segment.split('[')[0]}"
                
                if self.segment_is_indexable(segment):
                    if self.inputs[inp_index].index_type == "Blend Data":
                        data_path = self.inputs[inp_index].python_value
                    else:
                        data_path += f"[{self.inputs[inp_index].python_value}]"
                    inp_index += 1
                
                if segment == self.return_data:
                    break

            self.outputs[0].python_value = data_path


    def draw_node(self, context, layout):
        row = layout.row(align=True)
        row.scale_y = 1.5
        if self.get_data():
            row.prop(self, "return_data", text="")
            self.draw_data_select(row, text="")

            op = row.operator("sn.reset_data_path", text="", icon="LOOP_BACK")
            op.node_tree = self.node_tree.name
            op.node = self.name

            self.draw_data_type_not_set(layout)
            
        else:
            op = row.operator("sn.paste_data_path", text="Paste Property", icon="PASTEDOWN")
            op.node_tree = self.node_tree.name
            op.node = self.name

    def draw_node_panel(self, context, layout):
        layout.prop(self, "data_path")
        layout.label(text=str(self.get_data()))