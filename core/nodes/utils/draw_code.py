import bpy

from ....utils.code import normalize_indents


def draw_code(layout: bpy.types.UILayout, node: bpy.types.Node):
    """ Draws the node code """
    box = layout.box()
    col = box.column(align=True)
    lines = normalize_indents(node.code).split("\n")

    while lines and (not lines[0].strip() or not lines[-1].strip()):
        if not lines[0].strip():
            lines.pop(0)
        if not lines[-1].strip():
            lines.pop(-1)

    for line in lines:
        _draw_line(col, line, node)


def _draw_line(layout: bpy.types.UILayout, line: str, node: bpy.types.Node):
    """ Draws the node code """
    if "._execute_node(" in line:
        indents = len(line) - len(line.lstrip())
        id = line.split("._execute_node('")[1].split("',")[0]
        for n in node.node_tree.nodes:
            if n.get("id", None) == id:
                layout.label(text=" "*indents + f"{{Node '{n.name}'}}")
                break
        else:
            layout.label(text=line)
    else:
        layout.label(text=line)
