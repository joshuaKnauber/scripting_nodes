import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_RunPropertyFunctionNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RunPropertyFunctionNode"
    bl_label = "Run Property Function"
    node_color = "PROPERTY"
    
    
    def _disect_data_path(self, path):
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
        # segments[-1] = segments[-1].split("[")[0]
        return segments
    
    def _is_valid_data_path(self, path):
        return path and "bpy." in path and not ".ops." in path

    def get_data(self):
        if self._is_valid_data_path(self.pasted_data_path):
            return self._disect_data_path(self.pasted_data_path)
        return None
    
    
    def segment_is_indexable(self, segment):
        """ Returns if a segment can be indexed. A segment is a string part of a data path """
        return "[" in segment and "]" in segment
    
    def create_inputs_from_path(self):
        """ Creates the inputs for the given data path """
        self.inputs.clear()
        data = self.get_data()
        if data:
            for segment in data:
                if self.segment_is_indexable(segment):
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
            return self.pasted_data_path.split(".")[-1].replace("_", " ").title()
        return "Property Function"
    
    def on_prop_change(self, context):
        self.label = self.get_pasted_prop_name()
        self.create_inputs_from_path()
        self._evaluate(context)
        
    pasted_data_path: bpy.props.StringProperty(name="Pasted Path",
                                description="The full data path to the property",
                                update=on_prop_change)
    

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        
        
    def update_require_execute(self, context):
        self.inputs[0].set_hide(not self.require_execute)
        self.outputs[0].set_hide(not self.require_execute)
        self._evaluate(context)
        
    require_execute: bpy.props.BoolProperty(name="Require Execute", default=True,
                                        description="Removes the execute inputs and only gives you the return value",
                                        update=update_require_execute)


    def evaluate(self, context):
        if self.pasted_data_path:
            pass
        

    def draw_node(self, context, layout):
        row = layout.row(align=True)
        row.scale_y = 1.2
        op = row.operator("sn.paste_data_path", text=self.get_pasted_prop_name() if self.pasted_data_path else "Paste Function", icon="PASTEDOWN")
        op.node = self.name
        op.node_tree = self.node_tree.name
        if self.pasted_data_path:
            op = row.operator("sn.reset_data_path", text="", icon="LOOP_BACK")
            op.node = self.name
            op.node_tree = self.node_tree.name
            
            if len(self.outputs) > 1:
                layout.prop(self, "require_execute")
            
    def draw_node_panel(self, context, layout):
        layout.prop(self, "pasted_data_path", text="Function Path")