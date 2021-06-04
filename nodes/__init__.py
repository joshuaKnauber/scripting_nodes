import bpy
import os
from importlib import import_module
import inspect


from . import tutorial


classes = [tutorial.SN_OT_StartTutorial,
            tutorial.SN_OT_EndTutorial,
            tutorial.SN_OT_MoveTutorial,
            tutorial.SN_OT_SetTutorial,
            tutorial.SN_TutorialNode]


def get_node_classes():
    nodes = []
    for name in os.listdir(os.path.dirname(__file__)):
        if not "__pycache__" in name and not ".py" in name:
            for node_file in os.listdir(os.path.join(os.path.dirname(__file__), name)):
                if ".py" in node_file and not node_file == "__init__.py":

                    root = __name__.partition('.')[0]
                    module = import_module(f"{root}.nodes.{name}.{node_file.split('.')[0]}")
                    for value in module.__dict__.values():
                        if inspect.isclass(value):
                            if ".nodes." in str(value):
                                if hasattr(value, "bl_rna"):
                                    # print(value)
                                    nodes.append(value)
    # return []
    return nodes


def register():
    global classes
    for cls in classes + get_node_classes():
        bpy.utils.register_class(cls)


def unregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)