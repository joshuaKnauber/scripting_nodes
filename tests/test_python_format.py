"""lib/python_format.py: formatting like `ruff format` (the expected outputs
are ruff's) and removing redundant parentheses."""

import unittest

import helpers

SOURCE = r"""def f():
    return isinstance(node, BlendPathMixinxxxxxxxxxxxxxxxx) and getattr(node, 'mode', 'BLENDER') == 'BLENDER'
def g():
    return isinstance(node, BlendPathMixinxxxxxxxxxxxxxxxxxxxxxxxxxx) + getattr(node, "mode", "BLENDER")
class A(bpy.types.PropertyGroup):
    axis: bpy.props.EnumProperty(name='Axis', items=[
        ('X', 'X', ''),
        ('Y', 'Y', ''),
    ])
    sets: bpy.props.CollectionProperty(name='Sets', type=OBJECT_TOOLKIT_PG_selection_set_long_name)
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        layout.template_list("OBJECT_TOOLKIT_UL_sets", "", context.scene.object_toolkit, "sets", context.scene.object_toolkit, "active_set")
x = 'it\'s'
y = "say \"hi\""
"""

# uvx ruff format --isolated - < SOURCE
FORMATTED = r"""def f():
    return (
        isinstance(node, BlendPathMixinxxxxxxxxxxxxxxxx)
        and getattr(node, "mode", "BLENDER") == "BLENDER"
    )


def g():
    return isinstance(node, BlendPathMixinxxxxxxxxxxxxxxxxxxxxxxxxxx) + getattr(
        node, "mode", "BLENDER"
    )


class A(bpy.types.PropertyGroup):
    axis: bpy.props.EnumProperty(
        name="Axis",
        items=[
            ("X", "X", ""),
            ("Y", "Y", ""),
        ],
    )
    sets: bpy.props.CollectionProperty(
        name="Sets", type=OBJECT_TOOLKIT_PG_selection_set_long_name
    )

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_property, index
    ):
        layout.template_list(
            "OBJECT_TOOLKIT_UL_sets",
            "",
            context.scene.object_toolkit,
            "sets",
            context.scene.object_toolkit,
            "active_set",
        )


x = "it's"
y = 'say "hi"'
"""


def python_format():
    return helpers.sn("src.lib.python_format")


class PythonFormatTest(unittest.TestCase):
    def test_formats_like_ruff(self):
        self.assertEqual(python_format().format_source(SOURCE), FORMATTED)

    def test_formatted_code_stays_as_it_is(self):
        self.assertEqual(python_format().format_source(FORMATTED), FORMATTED)

    def test_quotes(self):
        normalize = python_format().normalize_string
        for text, expected in (
            ("'a'", '"a"'),
            ("'it\\'s'", '"it\'s"'),
            ('"say \\"hi\\""', "'say \"hi\"'"),
            ("'q\"'", "'q\"'"),
            ("f'{x}'", 'f"{x}"'),
            ("r'\\d'", 'r"\\d"'),
        ):
            self.assertEqual(normalize(text), expected)

    def test_redundant_parens(self):
        remove = python_format().remove_redundant_parens
        for code, expected in (
            (
                "x = ((a * b) if (c == 1) else (0.0))\n",
                "x = a * b if c == 1 else 0.0\n",
            ),
            ("f(((x)))\n", "f(x)\n"),
            ("m = (a + b) * c\n", "m = (a + b) * c\n"),
            # kept: they help reading or are needed
            ("y = not (a == b)\n", "y = not (a == b)\n"),
            ("z = a or (b and c)\n", "z = a or (b and c)\n"),
            ("t = (a, b)\n", "t = (a, b)\n"),
            ("w = (1).real\n", "w = (1).real\n"),
            ("g((x for x in y))\n", "g((x for x in y))\n"),
        ):
            self.assertEqual(remove(code), expected)
