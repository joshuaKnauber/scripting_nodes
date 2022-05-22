import json
import bpy
from ...nodes.base_node import SN_ScriptingBaseNode
    
    
    
class SN_OT_RemovePreset(bpy.types.Operator):
    bl_idname = "sn.remove_preset"
    bl_label = "Remove Preset"
    bl_description = "Removes this preset"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    index: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        prefs = bpy.context.preferences.addons[__name__.partition('.')[ 0]].preferences
        prefs.presets.remove(self.index)
        bpy.ops.wm.save_userpref()
        return {"FINISHED"}
    
    
    
class SN_OT_RemovePresets(bpy.types.Operator):
    bl_idname = "sn.remove_presets"
    bl_label = "Remove Presets"
    bl_description = "Remove presets"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        prefs = bpy.context.preferences.addons[__name__.partition('.')[ 0]].preferences
        layout.label(text="Presets")

        for i, preset in enumerate(prefs.presets):
            layout.operator("sn.remove_preset", text=f"Remove '{preset.name}'", icon="REMOVE").index = i

        if not len(prefs.presets):
            layout.label(text="No presets", icon="INFO")
    
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=300)



class SN_OT_AddPreset(bpy.types.Operator):
    bl_idname = "sn.add_preset"
    bl_label = "Add Preset"
    bl_description = "Adds the active node as a preset"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        return context.space_data.node_tree.nodes.active
    
    def get_save_value(self, data, attr):
        value = getattr(data, attr)
        if "bpy_prop_array" in str(type(value)) or "Color" in str(type(value)):
            return tuple(value)
        return value

    def execute(self, context):
        node = context.space_data.node_tree.nodes.active
        prefs = bpy.context.preferences.addons[__name__.partition('.')[ 0]].preferences
        
        item = prefs.presets.add()
        item.name = node.label if node.label else node.name
        item.idname = node.bl_idname
        
        data = { "node": {}, "inputs": [], "outputs": [] }
        
        # get node attributes
        attributes = [a for a in dir(node) if not callable(getattr(node, a))]
        data_attributes = ["width", "color", "use_custom_color"]
        for attr in attributes:
            if not attr.startswith("__") and not attr.startswith("bl_")\
                and not attr == "code" and not attr.startswith("code_") and not attr.startswith("ref_")\
                and not hasattr(SN_ScriptingBaseNode, attr) and not attr in bpy.types.Node.bl_rna.properties.keys()\
                and not attr in ["active_layout", "disable_evaluation", "skip_export", "static_uid",]:
                data_attributes.append(attr)

        # save node attributes
        for attr in data_attributes:
            data["node"][attr] = self.get_save_value(node, attr)

        socket_save_attributes = ["name", "disabled", "index_type", "data_type", "default_value"]
        # get input attributes
        for inp in node.inputs:
            input_data = {}
            if not inp.is_program:
                for attr in socket_save_attributes:
                    if hasattr(inp, attr):
                        input_data[attr] = self.get_save_value(inp, attr)
            data["inputs"].append(input_data)

        # get output attributes
        for out in node.outputs:
            output_data = {}
            if not out.is_program:
                for attr in socket_save_attributes:
                    if hasattr(out, attr):
                        output_data[attr] = self.get_save_value(out, attr)
            data["outputs"].append(output_data)
        
        item.data = json.dumps(data)

        bpy.ops.wm.save_userpref()
        return {"FINISHED"}



class SN_OT_LoadPreset(bpy.types.Operator):
    bl_idname = "sn.load_preset"
    bl_label = "Load Preset"
    bl_description = "Loads this preset node"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    index: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})
    
    def get_write_value(self, value):
        return list(value) if type(value) == list else value

    def execute(self, context):
        prefs = bpy.context.preferences.addons[__name__.partition('.')[ 0]].preferences
        preset = prefs.presets[self.index]
        
        bpy.ops.node.add_node("INVOKE_DEFAULT", type=preset.idname, use_transform=True)
        node = context.space_data.node_tree.nodes.active

        node.label = preset.name
        
        data = json.loads(preset.data)
        # load node data
        node.disable_evaluation = True
        for attr in data["node"].keys():
            setattr(node, attr, self.get_write_value(data["node"][attr]))

        # load input data
        for i, inp_data in enumerate(data["inputs"]):
            node.disable_evaluation = True
            for attr in inp_data.keys():
                setattr(node.inputs[i], attr, self.get_write_value(inp_data[attr]))
        
        # load output data
        for i, out_data in enumerate(data["outputs"]):
            node.disable_evaluation = True
            for attr in out_data.keys():
                setattr(node.outputs[i], attr, self.get_write_value(out_data[attr]))
        
        node.disable_evaluation = False
        node._evaluate(context)
        return {"FINISHED"}
