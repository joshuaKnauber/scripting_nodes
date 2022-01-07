import bpy
import re



def get_python_name(name, replacement="", separator="_"):
    """ Returns the given name as a valid python represention to use as variable names in scripts """
    # format string
    name = name.replace(" ", separator).lower()

    # remove non alpha characters at the start
    regex = re.compile('[^a-zA-Z_]')
    name = regex.sub('', name)
    
    # return string
    if not name:
        return replacement
    return name



class SN_OT_Tooltip(bpy.types.Operator):
    bl_idname = "sn.tooltip"
    bl_label = "Tooltip"
    bl_description = "Click to learn more"
    bl_options = {"REGISTER", "INTERNAL"}

    text: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.enabled = False
        row.label(text="Info")

        col = layout.column(align=True)
        for line in self.text.split("\n"):
            col.label(text=line)
    
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=500)
