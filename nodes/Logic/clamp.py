import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_ClampNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ClampNode"
    bl_label = "Clamp"
    # bl_icon = "GRAPH"
    bl_width_default = 160


    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_float_input("Value")
        inp = self.add_float_input("Min")
        inp.set_default(0)
        inp.disableable = True
        inp = self.add_float_input("Max")
        inp.set_default(1)
        inp.disableable = True
        
        self.add_float_output("Float Result")
        self.add_integer_output("Integer Result")


    def code_evaluate(self, context, touched_socket):
        n = self.inputs["Value"].code()
        smallest = self.inputs["Min"].code()
        largest = self.inputs["Max"].code()
        
        if not self.inputs["Min"].enabled:
            smallest = n
        if not self.inputs["Max"].enabled:
            largest = n
            
        if touched_socket == self.outputs[0]:
            return {
                "code": f"""float(max({smallest}, min({n}, {largest})))"""
            }
        else:
            return {
                "code": f"""int(max({smallest}, min({n}, {largest})))"""
            }