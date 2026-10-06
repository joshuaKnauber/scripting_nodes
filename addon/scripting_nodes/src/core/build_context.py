"""Build-time codegen flag.

True while the export builds a shippable addon. Node `generate()` methods can
check `is_building()` to strip dev-only affordances (SN overlay hooks,
debugger glue, ...) from the produced code.
"""

from contextlib import contextmanager

_is_building = False


def is_building() -> bool:
    return _is_building


@contextmanager
def building():
    global _is_building
    _is_building = True
    try:
        yield
    finally:
        _is_building = False
