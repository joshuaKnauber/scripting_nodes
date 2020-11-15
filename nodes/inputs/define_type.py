#SN_DefineTypeNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode

class SN_DefineTypeNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DefineTypeNode"
    bl_label = "Define Type"
    bl_icon = "MESH_CUBE"
    node_color = (0.53, 0.55, 0.53)
    bl_width_default = 180
    should_be_registered = False

    docs = {
        "text": ["This node is used to <important>change the default properties coming from modifier into specific properties of the modifier type</>.",
                "Object Input: The input of the Modifier whos properties you want to change",
                "Modifier Input: The input of the Modifier whos properties you want to change",
                "Modifier Output: The output of the Modifier",
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

    def get_nodes(self, context):
        compositor = []
        shader = []
        texture = []

        for class_type in dir(bpy.types):
            if "Node" in class_type:
                if not "Tree" in class_type and not "Editor" in class_type:
                    if not class_type in ["Node","Nodes","NodeCustomGroup","NodeFrame","NodeGroup","NodeGroupInput","NodeGroupOutput","NodeInputs","NodeInstanceHash","NodeInternal","NodeInternalSocketTemplate","NodeLink","NodeLinks","NodeOutputs","NodeReroute","NodeSocket","TextureNode","CompositorNode","ShaderNode"]:
                        if not "Socket" in class_type:
                            if "Compositor" in class_type:
                                if class_type == "CompositorNodeOutputFileLayerSlots":
                                    compositor.append(("bpy.types.CompositorNodeOutputFileLayerSlots", "File Layer Output Slots", ""))
                                else:
                                    compositor.append(("bpy.types." + class_type, (eval("bpy.types." + class_type).bl_rna.name), ""))
                            elif "Shader" in class_type:
                                shader.append(("bpy.types." + class_type, (eval("bpy.types." + class_type).bl_rna.name), ""))
                            elif "Texture" in class_type:
                                texture.append(("bpy.types." + class_type, (eval("bpy.types." + class_type).bl_rna.name), ""))

        if self.node_type == "compositor":
            return compositor
        elif self.node_type == "shader":
            return shader
        else:
            return texture
    
    def get_nodesockets(self, context):
        sockets = []
        socket_names = []

        for class_type in dir(bpy.types):
            if "NodeSocket" in class_type and not class_type in ["NodeSocket"]:
                if not eval("bpy.types." + class_type).bl_rna.name.replace(" Node Socket", "") in socket_names:
                    if not eval("bpy.types." + class_type).bl_rna.name.replace(" Node Socket", "") in ['Node Socket Template', 'Boolean Interface', 'Color Interface', 'Float Interface', 'Integer Interface', 'Shader Interface', 'NodeSocketInterfaceStandard', 'String Interface', 'Vector Interface', "NodeSocketStandard", "Virtual"]:
                        sockets.append(("bpy.types." + eval("bpy.types." + class_type).bl_rna.identifier, eval("bpy.types." + class_type).bl_rna.name.replace(" Node Socket", ""), ""))
                        socket_names.append(eval("bpy.types." + class_type).bl_rna.name.replace(" Node Socket", ""))

        return sockets

    def get_objects(self, context):
        items = []
        items.append(('bpy.types.Mesh', "Mesh", ""))
        items.append(("bpy.types.Light", "Light", ""))
        items.append(("bpy.types.Camera", "Camera", ""))
        items.append(("bpy.types.GreasePencil", "GPencil", ""))
        items.append(("bpy.types.Armature", "Armature", ""))
        items.append(("BlendDataProbes", "Probe", ""))
        items.append(("bpy.types.Speaker", "Speaker", ""))
        items.append(("bpy.types.Curve", "Curve", ""))
        items.append(("bpy.types.BlendDataFonts", "Font", ""))
        items.append(("bpy.types.Volume", "Volume", ""))
        items.append(("bpy.types.Lattice", "Lattice", ""))

        return items


    def update_output(self, context):
        if len(self.outputs) == 1:
            if self.outputs[0].is_linked:
                self.outputs[0].links[0].to_node.reset_data_type(None)

    modifier_type: bpy.props.EnumProperty(items=[("object", "Object", ""), ("gpencil", "GPencil", ""), ("linestyle", "LineStyle", ""), ("fcurve", "F-Curve", ""), ("other", "Other", "")], name="Type", description="The type of the modifier type you want to output", update=update_output)
    modifier: bpy.props.EnumProperty(items=get_modifiers, name="Modifier", description="The modifier you want to output", update=update_output)
    light: bpy.props.EnumProperty(items=[("bpy.types.PointLight", "Point", ""), ("bpy.types.SunLight", "Sun", ""), ("bpy.types.SpotLight", "Spot", ""), ("bpy.types.AreaLight", "Area", "")], name="Light", description="The light type you want to output", update=update_output)
    node_type: bpy.props.EnumProperty(items=[("compositor", "Compositor", ""), ("shader", "Shader", ""), ("texture", "Texture", "")], name="Node Type", description="The node type", update=update_output)
    node: bpy.props.EnumProperty(items=get_nodes, name="Node", description="The node type you want to output", update=update_output)
    node_socket: bpy.props.EnumProperty(items=get_nodesockets, name="NodeSocket", description="The nodesocket type you want to output", update=update_output)
    object_type: bpy.props.EnumProperty(items=get_objects, name="Object Type", description="The objects type", update=update_output)


    def inititialize(self,context):
        self.sockets.create_input(self,"OBJECT", "Type")
        self.sockets.create_output(self, "OBJECT", "Defined Type")

    def get_data_type(self):
        return self.inputs[0].links[0].from_node.data_type(self.inputs[0].links[0].from_socket)

    def update_node(self):
        if len(self.inputs) == 1:
            if len(self.inputs[0].links) == 1:
                if not self.get_data_type() in ["bpy.types.Modifier", "bpy.types.Light", "bpy.types.Node", "bpy.types.NodeSocket", "bpy.types.Object"]:
                    link = self.inputs[0].links[0]
                    bpy.context.space_data.node_tree.links.remove(link)

    def draw_buttons(self, context, layout):
        if len(self.inputs) == 1:
            if len(self.inputs[0].links) == 1:
                if self.get_data_type() == "bpy.types.Modifier":
                    layout.prop(self, "modifier_type")
                    layout.prop(self, "modifier")
                elif self.get_data_type() == "bpy.types.Light":
                    layout.prop(self, "light")
                elif self.get_data_type() == "bpy.types.Node":
                    layout.prop(self, "node_type")
                    layout.prop(self, "node")
                elif self.get_data_type() == "bpy.types.NodeSocket":
                    layout.prop(self, "node_socket")
                elif self.get_data_type() == "bpy.types.Object":
                    layout.prop(self, "object_type")
            else:
                box = layout.box()
                box.label(text="Connect one of the following:")
                box.label(text="Object, Modifier, Light, Node, NodeSocket")

    def evaluate(self, socket, node_data, errors):
        if len(self.inputs[0].links) == 1:
            if self.get_data_type() in ["bpy.types.Modifier", "bpy.types.Light", "bpy.types.Node", "bpy.types.NodeSocket", "bpy.types.Object"]:
                return {"blocks": [{"lines": [[node_data["input_data"][0]["code"]]],"indented": []}],"errors": errors}
        errors.append({"title": "No input provided", "message": "You need to put in the type you want to define", "node": self, "fatal": True})
        return {"blocks": [{"lines": [],"indented": []}],"errors": errors}

    def data_type(self, output):
        if len(self.inputs) == 1:
            if len(self.inputs[0].links) == 1:
                if self.get_data_type() == "bpy.types.Modifier":
                    return self.modifier
                elif self.get_data_type() == "bpy.types.Light":
                    return self.light
                elif self.get_data_type() == "bpy.types.Node":
                    return self.node
                elif self.get_data_type() == "bpy.types.NodeSocket":
                    return self.node_socket
                elif self.get_data_type() == "bpy.types.Object":
                    return self.object_type
                
        return ""

