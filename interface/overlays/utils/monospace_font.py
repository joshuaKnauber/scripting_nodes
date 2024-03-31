import os
import blf

_monospace_font_id = 0


def get_monospace_font() -> int:
    """Loads the blender monospace font if not already loaded and returns the id"""
    global _monospace_font_id
    if not _monospace_font_id:
        font_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            "assets",
            "fonts",
            "DejaVuSansMono.woff2",
        )
        _monospace_font_id = blf.load(font_path)
    return _monospace_font_id
