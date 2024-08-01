import bpy
from itertools import chain


# Credit to https://github.com/nortikin/sverchok/blob/6db84ff4c0c0f56976d587b8b4b86a779bb9da49/data_structure.py
def extend_blender_class(cls):
    """
    It is class decorator for adding extra logic into base Blender classes
    Decorated class should have the same name as Blender class
    Take into account that this decorator does not delete anything onto reload event
    """
    bl_class = getattr(bpy.types, cls.__name__)
    for base_cls in chain([cls], cls.__bases__):
        # https://docs.python.org/3/howto/annotations.html#accessing-the-annotations-dict-of-an-object-in-python-3-9-and-older
        # avoiding getting inherited annotations
        if "__annotations__" in base_cls.__dict__:
            for name, prop in base_cls.__dict__["__annotations__"].items():
                setattr(bl_class, name, prop)
        for key in (key for key in dir(base_cls) if not key.startswith("_")):
            setattr(bl_class, key, getattr(base_cls, key))
    return cls
