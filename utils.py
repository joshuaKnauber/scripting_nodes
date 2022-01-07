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





def get_indents(line):
    """ Returns the amount of spaces at the start of the given line """
    return len(line) - len(line.lstrip())

def get_min_indent(code_lines):
    """ Returns the minimum indent of the given lines of text """
    min_indent = 9999
    for line in code_lines:
        if not line.isspace() and line:
            min_indent = min(min_indent, get_indents(line))
    return min_indent if min_indent != 9999 else 0

def normalize_code(raw_code):
    """ Normalizes the given code to the minimum indent and removes empty lines """
    lines = raw_code.split("\n")
    min_indent = get_min_indent(lines)
    indented = []
    for line in lines:
        new_line = line[min_indent:]
        if new_line:
            indented.append(new_line)
    return "\n".join(indented)



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
