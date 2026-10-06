"""Build-time codegen flag.

Set to True by the export operator while it's emitting files for a
shippable addon, False the rest of the time. Node `generate()` methods can
check `is_building()` to strip dev-only affordances (SN overlay hooks,
debugger glue, etc.) from the produced code.
"""

_is_building = False


def is_building() -> bool:
    return _is_building


def set_building(value: bool) -> None:
    global _is_building
    _is_building = bool(value)
