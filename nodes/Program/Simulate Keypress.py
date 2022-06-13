import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_SimulateKeypressNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SimulateKeypressNode"
    bl_label = "Simulate Keypress"
    bl_width_default = 200
    node_color = "PROGRAM"
    
    key: bpy.props.StringProperty(name="Key", default="Y", update=SN_ScriptingBaseNode._evaluate)

    recording: bpy.props.BoolProperty(name="Recording", default=False)
    
    def on_create(self, context):
        self.add_execute_input()
        self.add_boolean_input('Shift')
        self.add_boolean_input('Ctrl')
        self.add_boolean_input('Alt')
        self.add_boolean_input('OS Key')
        self.add_execute_output()
        
    def draw_node(self, context, layout):
        layout.operator("sn.record_key", text=self.key, depress=self.recording).node = self.name

    def evaluate(self, context):
        self.code_imperative = """
            def run_operator_from_keypress(area_type, event_type, shift, ctrl, alt, oskey):
                options = []
                for keymap in bpy.context.window_manager.keyconfigs.user.keymaps:
                    if area_type == keymap.space_type or keymap.space_type == "EMPTY":
                        for item in keymap.keymap_items:
                            if item.type == event_type and item.shift == shift and item.ctrl == ctrl and item.alt == alt and item.oskey == oskey:
                                if item.idname:
                                    props = ""
                                    if item.properties:
                                        for prop in item.properties.keys():
                                            print(item.properties[prop])
                                            print(type(item.properties[prop]))
                                            if type(item.properties[prop]) == str:
                                                props += f"{prop}='{item.properties[prop]}', "
                                            else:
                                                props += f"{prop}={item.properties[prop]}, "
                                    op = f"bpy.ops.{item.idname}('INVOKE_DEFAULT', {props})"
                                    options.append((op, keymap.space_type))
                                    # eval(op)
                                    # return
                print(options)
        """
        self.code = f"""
                    run_operator_from_keypress(bpy.context.area.type, '{self.key}', {self.inputs['Shift'].python_value}, {self.inputs['Ctrl'].python_value}, {self.inputs['Alt'].python_value}, {self.inputs['OS Key'].python_value})
                    {self.indent(self.outputs[0].python_value, 5)}
                    """