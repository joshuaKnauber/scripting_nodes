#SN_SetModifierNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode

class SN_SetModifierNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SetModifierNode"
    bl_label = "Set Modifier"
    bl_icon = "MESH_CUBE"
    node_color = (0.53, 0.55, 0.53)
    bl_width_default = 180
    should_be_registered = False

    docs = {
        "text": ["This node is used to <important>change the default properties coming from modifier into specific properties of the modifier type</>.",
                "Modifier Input: The input of the Modifier whos properties you want to change",
                "Modifier Input: The output of the Modifier",
                ""],
        "python": []

    }

    def reset_data_type(self, context):
        self.update_node()

    def get_modifiers(self, context):
        gpencil = []
        obj = []
        linestyle = []
        fcurve = ['FModifierCycles','FModifierEnvelope','FModifierEnvelopeControlPoint','FModifierEnvelopeControlPoints','FModifierFunctionGenerator','FModifierGenerator','FModifierLimits','FModifierNoise','FModifierPython','FModifierStepped']
        other = ['BrightContrastModifier','ColorBalanceModifier','CurveModifier','CurvesModifier','HueCorrectModifier','SequenceModifier','SequencerTonemapModifierData','WhiteBalanceModifier']


        for class_type in dir(bpy.types):
            if "Modifier" in class_type and not "Modifiers" in class_type:
                if not class_type in ["GpencilModifier", "Modifier", "FModifier"]:
                    if "gpencil" in class_type.lower():
                        gpencil.append(class_type)
                    elif "linestyle" in class_type.lower():
                        linestyle.append(class_type)
                    elif not class_type in fcurve and not class_type in other:
                        obj.append(class_type)

        modifiers = []
        if self.modifier_type == "gpencil":
            for mod in gpencil:
                modifiers.append(("bpy.types."+mod, eval("bpy.types."+mod+".bl_rna.name").replace(" Modifier", ""), ""))
        elif self.modifier_type == "object":
            for mod in obj:
                modifiers.append(("bpy.types."+mod, eval("bpy.types."+mod+".bl_rna.name").replace(" Modifier", ""), ""))
        elif self.modifier_type == "linestyle":
            for mod in linestyle:
                modifiers.append(("bpy.types."+mod, eval("bpy.types."+mod+".bl_rna.name").replace(" Modifier", ""), ""))
        elif self.modifier_type == "fcurve":
            for mod in fcurve:
                modifiers.append(("bpy.types."+mod, eval("bpy.types."+mod+".bl_rna.name").replace(" Modifier", ""), ""))
        else:
            for mod in other:
                modifiers.append(("bpy.types."+mod, eval("bpy.types."+mod+".bl_rna.name").replace(" Modifier", ""), ""))

        return modifiers

    def update_modifier(self, context):
        if len(self.outputs) == 1:
            if self.outputs[0].is_linked:
                self.outputs[0].links[0].to_node.reset_data_type(None)

    modifier_type: bpy.props.EnumProperty(items=[("object", "Object", ""), ("gpencil", "GPencil", ""), ("linestyle", "LineStyle", ""), ("fcurve", "F-Curve", ""), ("other", "Other", "")], name="Type", description="The type of the modifier you want to output", update=update_modifier)
    modifier: bpy.props.EnumProperty(items=get_modifiers, name="Modifier", description="The modifier you want to output", update=update_modifier)

    def inititialize(self,context):
        self.sockets.create_input(self,"OBJECT","Modifier")
        self.sockets.create_output(self, "OBJECT", "Modifier")

    def get_data_type(self):
        return self.inputs[0].links[0].from_node.data_type(self.inputs[0].links[0].from_socket)

    def update_node(self):
        if len(self.inputs) == 1:
            if len(self.inputs[0].links) == 1:
                if self.get_data_type() != "bpy.types.Modifier":
                    link = self.inputs[0].links[0]
                    bpy.context.space_data.node_tree.links.remove(link)

    def draw_buttons(self, context, layout):
        if len(self.inputs) == 1:
            if len(self.inputs[0].links) == 1:
                if self.get_data_type() == "bpy.types.Modifier":
                    layout.prop(self, "modifier_type")
                    layout.prop(self, "modifier")

    def evaluate(self, socket, node_data, errors):
        if len(self.inputs[0].links) == 1:
            if self.get_data_type() == "bpy.types.Modifier":
                return {"blocks": [{"lines": [[node_data["input_data"][0]["code"]]],"indented": []}],"errors": errors}
        errors.append({"title": "No modifier provided", "message": "You need to put in the modifier whos properties you want to get", "node": self, "fatal": True})
        return {"blocks": [{"lines": [],"indented": []}],"errors": errors}

    def data_type(self, output):
        if len(self.inputs) == 1:
            if len(self.inputs[0].links) == 1:
                if self.get_data_type() == "bpy.types.Modifier":
                    return self.modifier
        return ""

