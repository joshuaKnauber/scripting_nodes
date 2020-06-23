import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_CreateProperty(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CreateProperty"
    bl_label = "Create Property"
    bl_icon = node_icons["OPERATOR"]
    bl_width_default = 300
    _should_be_registered = True

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def getTypes(self, context):
        types = []
        for data in dir(bpy.data):
            if data != "linestyles":
                has_new = False
                try:
                    eval("bpy.data."+data+".new")
                    has_new = True
                except AttributeError:
                        pass
                if has_new:
                    types.append(data)

        for i, type_name in enumerate(types):
            type_name = type(eval("bpy.data.bl_rna.properties[\""+ type_name + "\"].fixed_type")).bl_rna
            types[i] = (type_name.identifier, type_name.identifier, type_name.description)

        return types

    propName: bpy.props.StringProperty(name="Name", description="Name of the property", default="My Property", update=socket_update)
    propDescription: bpy.props.StringProperty(name="Description", description="Description of the property", default="My Description", update=socket_update)
    propType: bpy.props.EnumProperty(items=[("BoolProperty", "Boolean", "A boolean input"), ("EnumProperty", "List", "A dropdown list that can be converted to display all values"), ("FloatProperty", "Numbers", "A input for all numbers"), ("IntProperty", "Whole Numbers", "A input for whole numbers"), ("StringProperty", "Text", "A text input")], name="Type", description="The type of the property", update=socket_update)
    propLocation: bpy.props.EnumProperty(items=getTypes, name="Location", description="", default=None, update=socket_update, get=None, set=None)


    propBool: bpy.props.EnumProperty(items=[("True", "True", ""), ("False", "False", "")], name="Default", description="The default value", update=socket_update)
    propString: bpy.props.StringProperty(name="", description="The default value", default="Default", update=socket_update)
    propFloat: bpy.props.FloatProperty(name="", description="The default value", default=0.0, update=socket_update)
    propInt: bpy.props.IntProperty(name="", description="The default value", default=0, update=socket_update)
    propEnum: bpy.props.StringProperty(name="", description="The default value", update=socket_update)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

    def draw_buttons(self, context, layout):
        layout.prop(self,"propType")
        layout.prop(self,"propLocation")
        layout.prop(self,"propName")
        layout.prop(self,"propDescription")
        if self.propType == "BoolProperty":
            layout.label(text="Default:")
            layout.prop(self, "propBool", expand=True)
        elif self.propType == "StringProperty":
            layout.label(text="Default:")
            layout.prop(self, "propString")
        elif self.propType == "FloatProperty":
            layout.label(text="Default:")
            layout.prop(self, "propFloat")
        elif self.propType == "IntProperty":
            layout.label(text="Default:")
            layout.prop(self, "propInt")
        elif self.propType == "EnumProperty":
            layout.label(text="Items (Seperate Items with commas):")
            layout.prop(self, "propEnum")

    def needed_imports(self):
        return ["bpy"]

    def get_register_block(self):
        name = self.ErrorHandler.handle_text(self.propName)
        code = "bpy.types." + self.propLocation + "." + name + " = bpy.props." + self.propType + "(name=\"" + self.propName + "\", description=\"" + self.propDescription + "\""
        if self.propType == "BoolProperty":
            code+=", default="
            code+=self.propBool
            code+=")"

        elif self.propType == "StringProperty":
            code+=", default=\""
            code+=self.propString
            code+="\")"

        elif self.propType == "FloatProperty":
            code+=", default="
            code+=str(self.propFloat)
            code+=")"

        elif self.propType == "IntProperty":
            code+=", default="
            code+=str(self.propInt)
            code+=")"

        elif self.propType == "EnumProperty":
            code+=", items="
            items = self.propEnum.split(",")
            newItems=[]
            for item in items:
                item = item.strip()
                newItems.append((item, item, ""))
            code+=str(newItems)
            code+=")"

        return [code]

    def get_unregister_block(self):
        name = self.ErrorHandler.handle_text(self.propName)
        return ["del bpy.types." + self.propLocation + "." + name]

    def evaluate(self, output):
        return {
            "blocks": [
                {
                    "lines": [],
                    "indented": []
                }
            ],
            "errors": []
        }
    
