import bpy
import re


def collection_has_item(collection, name):
    """Check if a CollectionProperty contains an item with the given name.
    
    This is needed for Blender 5.0+ compatibility where 'name in collection' 
    and 'collection.keys()' no longer work with custom get/set on the name property.
    """
    for item in collection:
        if item.name == name:
            return True
    return False


def collection_get_item(collection, name):
    """Get an item from a CollectionProperty by name.
    
    This is needed for Blender 5.0+ compatibility where 'collection[name]' 
    no longer works with custom get/set on the name property.
    Returns None if not found.
    """
    for item in collection:
        if item.name == name:
            return item
    return None


def get_python_name(name, replacement="", separator="_", lower=True):
    """ Returns the given name as a valid python represention to use as variable names in scripts """
    # format string
    name = name.replace(" ", separator)
    if lower:
        name = name.lower()

    # Remove invalid characters
    name = re.sub('[^0-9a-zA-Z_]', '', name)

    # Remove leading characters until we find a letter or underscore
    name = re.sub('^[^a-zA-Z]+', '', name)
    
    # return string
    if not name:
        return replacement
    return name



def unique_collection_name(name, default, name_list, separator="", includes_name=False):
    """ Returns a unique name based for the given list of names """
    if not name:
        name = default

    if name in name_list and includes_name:
        name_list.remove(name)
        
    if name in name_list:
        number = 1
        if len(name) > 3 and name[-3:].isdigit() and name[-4] == separator:
            name = name[:-4]
        while f"{name}{separator}{str(number).zfill(3)}" in name_list:
            number += 1
        
        name = f"{name}{separator}{str(number).zfill(3)}"
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


def indent_code(code, indents, start_line_index=1):
    """ Indents the given code by the given amount of indents. Use this when inserting multiline blocks into code """
    # join code blocks if given
    if type(code) == list:
        code = "\n".join(code)

    # split code and indent properly
    lines = code.split("\n")
    for i in range(start_line_index, len(lines)):
        lines[i] = " "*(4*indents) + lines[i]
    return "\n".join(lines)



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
