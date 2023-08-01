import blf
import bpy

_errors = []


def display_error(error: str):
    """ Adds an error to the interface """
    global _errors
    if error in _errors:
        _errors.remove(error)
    _errors.insert(0, error)
    _errors = _errors[-5:]


def draw_errors():
    """ Draws the errors to the interface """
    global _errors
    font_id = 0
    blf.size(font_id, 20)
    blf.enable(font_id, blf.WORD_WRAP)
    blf.word_wrap(font_id, 800)
    top = 40
    left = 40
    for i, error in enumerate(_errors):
        blf.color(font_id, 1, 1, 1, 1 - i*0.2)
        blf.position(font_id, left, bpy.context.region.height - top, 0)
        blf.draw(font_id, error)
        _, height = blf.dimensions(font_id, error)
        top += height + 20
    blf.disable(font_id, blf.WORD_WRAP)
